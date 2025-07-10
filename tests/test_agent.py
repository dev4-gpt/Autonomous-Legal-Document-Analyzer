"""
Tests for the legal analysis agent module.
"""

import pytest
from unittest.mock import Mock, patch

from src.core.agent import LegalAnalysisAgent, AnalysisResult, analyze_document


class TestLegalAnalysisAgent:
    """Test cases for LegalAnalysisAgent class."""
    
    def test_init(self):
        """Test agent initialization."""
        agent = LegalAnalysisAgent()
        assert agent.clause_types
        assert agent.contract_types
        assert agent.risk_levels
        assert agent.executor is not None
    
    def test_extract_field(self):
        """Test field extraction from LLM response."""
        agent = LegalAnalysisAgent()
        
        text = """
        CLASSIFICATION: NDA
        CONFIDENCE: 0.85
        REASONING: This appears to be a non-disclosure agreement.
        """
        
        classification = agent._extract_field(text, "CLASSIFICATION", "Unknown")
        confidence = agent._extract_field(text, "CONFIDENCE", "0.0")
        reasoning = agent._extract_field(text, "REASONING", "No reasoning")
        missing = agent._extract_field(text, "MISSING", "default")
        
        assert classification == "NDA"
        assert confidence == "0.85"
        assert "non-disclosure" in reasoning
        assert missing == "default"
    
    def test_calculate_overall_risk_empty(self):
        """Test overall risk calculation with empty risks."""
        agent = LegalAnalysisAgent()
        result = agent._calculate_overall_risk({})
        assert result == "Unknown"
    
    def test_calculate_overall_risk_mixed(self):
        """Test overall risk calculation with mixed risk levels."""
        agent = LegalAnalysisAgent()
        risks = {
            "Termination": "High",
            "Confidentiality": "Low",
            "Liability": "Medium",
            "Payment": "Critical"
        }
        result = agent._calculate_overall_risk(risks)
        assert result in ["High", "Critical"]  # Should be high due to Critical and High risks
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        agent = LegalAnalysisAgent()
        
        contract_type = {"confidence": 0.8}
        clauses = {"Termination": "text1", "Liability": "text2"}  # 2 out of 10 default clauses
        risks = {"Termination": "High", "Liability": "Medium"}  # All risks assessed
        
        score = agent._calculate_confidence_score(contract_type, clauses, risks)
        
        # Should be average of: 0.8 (classification) + 0.2 (clause success) + 1.0 (risk success)
        expected = (0.8 + 0.2 + 1.0) / 3
        assert abs(score - expected) < 0.01
    
    def test_get_risk_distribution(self):
        """Test risk distribution calculation."""
        agent = LegalAnalysisAgent()
        risks = {
            "Clause1": "High",
            "Clause2": "Low",
            "Clause3": "High",
            "Clause4": "Medium"
        }
        
        distribution = agent._get_risk_distribution(risks)
        expected = {"High": 2, "Low": 1, "Medium": 1}
        assert distribution == expected
    
    @patch('src.core.agent.llm_manager')
    def test_classify_contract(self, mock_llm_manager, sample_contract_text):
        """Test contract classification."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = """
        CLASSIFICATION: NDA
        CONFIDENCE: 0.9
        REASONING: This is clearly a confidentiality agreement.
        """
        mock_response.error = None
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._classify_contract(sample_contract_text)
        
        assert result["classification"] == "NDA"
        assert result["confidence"] == 0.9
        assert "confidentiality" in result["reasoning"]
    
    @patch('src.core.agent.llm_manager')
    def test_classify_contract_error(self, mock_llm_manager, sample_contract_text):
        """Test contract classification with LLM error."""
        # Mock LLM error
        mock_response = Mock()
        mock_response.error = "LLM failed"
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._classify_contract(sample_contract_text)
        
        assert result["classification"] == "Other"
        assert result["confidence"] == 0.0
        assert "failed" in result["reasoning"]
    
    @patch('src.core.agent.llm_manager')
    def test_extract_single_clause(self, mock_llm_manager, sample_contract_text):
        """Test single clause extraction."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "The Receiving Party agrees to keep all information confidential."
        mock_response.error = None
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._extract_single_clause("Confidentiality", sample_contract_text)
        
        assert "confidential" in result
        mock_llm_manager.invoke.assert_called_once()
    
    @patch('src.core.agent.llm_manager')
    def test_extract_single_clause_not_found(self, mock_llm_manager, sample_contract_text):
        """Test clause extraction when clause not found."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "NOT FOUND"
        mock_response.error = None
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._extract_single_clause("Indemnity", sample_contract_text)
        
        assert result == "NOT FOUND"
    
    @patch('src.core.agent.llm_manager')
    def test_assess_single_risk(self, mock_llm_manager):
        """Test single risk assessment."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = """
        RISK_LEVEL: High
        RISK_SCORE: 0.8
        RATIONALE: This clause has broad termination rights.
        """
        mock_response.error = None
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._assess_single_risk("Termination", "Either party may terminate at will.")
        
        assert result["risk_level"] == "High"
        assert "termination" in result["rationale"]
    
    @patch('src.core.agent.llm_manager')
    def test_summarize_contract(self, mock_llm_manager, sample_contract_text):
        """Test contract summarization."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "This is a confidentiality agreement between two parties."
        mock_response.error = None
        mock_llm_manager.invoke.return_value = mock_response
        
        agent = LegalAnalysisAgent()
        result = agent._summarize_contract(sample_contract_text)
        
        assert "confidentiality" in result
        mock_llm_manager.invoke.assert_called_once()
    
    @patch('src.core.agent.llm_manager')
    def test_analyze_contract_success(self, mock_llm_manager, sample_contract_text):
        """Test successful contract analysis."""
        # Mock all LLM responses
        def mock_invoke(prompt):
            mock_response = Mock()
            mock_response.error = None
            
            if "classify" in prompt.lower() or "classification" in prompt.lower():
                mock_response.content = """
                CLASSIFICATION: NDA
                CONFIDENCE: 0.9
                REASONING: This is a confidentiality agreement.
                """
            elif "confidentiality" in prompt.lower():
                mock_response.content = "The Receiving Party agrees to keep information confidential."
            elif "risk" in prompt.lower():
                mock_response.content = """
                RISK_LEVEL: Medium
                RATIONALE: Standard confidentiality clause with reasonable terms.
                """
            elif "summary" in prompt.lower():
                mock_response.content = "This is a standard confidentiality agreement."
            else:
                mock_response.content = "NOT FOUND"
            
            return mock_response
        
        mock_llm_manager.invoke.side_effect = mock_invoke
        
        agent = LegalAnalysisAgent()
        result = agent.analyze_contract(sample_contract_text, "test_doc_123")
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True
        assert result.doc_id == "test_doc_123"
        assert result.contract_type == "NDA"
        assert result.summary
        assert result.processing_time > 0
        assert result.confidence_score > 0
    
    @patch('src.core.agent.llm_manager')
    def test_analyze_contract_failure(self, mock_llm_manager, sample_contract_text):
        """Test contract analysis with failure."""
        # Mock LLM failure
        mock_llm_manager.invoke.side_effect = Exception("LLM service unavailable")
        
        agent = LegalAnalysisAgent()
        result = agent.analyze_contract(sample_contract_text, "test_doc_123")
        
        assert isinstance(result, AnalysisResult)
        assert result.success is False
        assert result.error_message is not None
        assert "LLM service unavailable" in result.error_message


class TestAnalyzeDocument:
    """Test cases for the analyze_document convenience function."""
    
    @patch('src.core.agent.legal_agent')
    def test_analyze_document_function(self, mock_agent, sample_contract_text):
        """Test the analyze_document convenience function."""
        # Mock agent response
        mock_result = AnalysisResult(
            doc_id="test123",
            contract_type="NDA",
            summary="Test summary",
            clauses={"Confidentiality": "Test clause"},
            risks={"Confidentiality": "Low"},
            risk_rationales={"Confidentiality": "Standard clause"},
            overall_risk_level="Low",
            confidence_score=0.8,
            processing_time=1.0,
            metadata={}
        )
        mock_agent.analyze_contract.return_value = mock_result
        
        result = analyze_document(sample_contract_text, "test123")
        
        assert isinstance(result, AnalysisResult)
        assert result.doc_id == "test123"
        mock_agent.analyze_contract.assert_called_once_with(sample_contract_text, "test123")


class TestAnalysisResult:
    """Test cases for AnalysisResult dataclass."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult creation."""
        result = AnalysisResult(
            doc_id="test123",
            contract_type="NDA",
            summary="Test summary",
            clauses={"Confidentiality": "Test clause"},
            risks={"Confidentiality": "Low"},
            risk_rationales={"Confidentiality": "Standard"},
            overall_risk_level="Low",
            confidence_score=0.8,
            processing_time=1.0,
            metadata={"test": "value"}
        )
        
        assert result.doc_id == "test123"
        assert result.contract_type == "NDA"
        assert result.success is True  # Default value
        assert result.error_message is None  # Default value
    
    def test_analysis_result_with_error(self):
        """Test AnalysisResult with error."""
        result = AnalysisResult(
            doc_id="test123",
            contract_type="Unknown",
            summary="",
            clauses={},
            risks={},
            risk_rationales={},
            overall_risk_level="Unknown",
            confidence_score=0.0,
            processing_time=0.5,
            metadata={},
            success=False,
            error_message="Analysis failed"
        )
        
        assert result.success is False
        assert result.error_message == "Analysis failed"
