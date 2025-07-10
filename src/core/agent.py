"""
Enhanced Legal Analysis Agent for the Legal Document Analyzer.
Provides comprehensive contract analysis with clause extraction, risk assessment, and classification.
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.prompts import PromptTemplate

from src.config import config
from src.utils import logger, analysis_logger, performance_logger
from src.database import Analysis, Clause, RiskAssessment, with_db_session
from .llm_manager import llm_manager, LLMResponse


@dataclass
class AnalysisResult:
    """Complete analysis result for a legal document."""
    doc_id: str
    contract_type: str
    summary: str
    clauses: Dict[str, str]
    risks: Dict[str, str]
    risk_rationales: Dict[str, str]
    overall_risk_level: str
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None


class LegalAnalysisAgent:
    """Advanced legal document analysis agent."""
    
    def __init__(self):
        self.clause_types = config.DEFAULT_CLAUSES
        self.contract_types = config.CONTRACT_TYPES
        self.risk_levels = config.RISK_LEVELS
        self.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize prompt templates for different analysis tasks."""
        
        # Contract classification prompt
        self.classify_prompt = PromptTemplate(
            input_variables=["contract_text", "contract_types"],
            template="""
            Analyze the following legal contract and classify it into one of these categories: {contract_types}
            
            Consider the following factors:
            - Primary purpose and subject matter
            - Key obligations and rights
            - Legal structure and terminology
            - Standard clauses and provisions
            
            Contract Text:
            {contract_text}
            
            Classification: Provide only the category name from the list above.
            Confidence: Rate your confidence from 0.0 to 1.0
            Reasoning: Provide a brief explanation for your classification.
            
            Format your response as:
            CLASSIFICATION: [category]
            CONFIDENCE: [score]
            REASONING: [explanation]
            """
        )
        
        # Clause extraction prompt
        self.clause_prompt = PromptTemplate(
            input_variables=["clause_type", "contract_text"],
            template="""
            Extract the {clause_type} clause from the following legal contract.
            
            Instructions:
            - Find the specific section or paragraph that deals with {clause_type}
            - Include the complete clause text, not just a summary
            - If multiple related clauses exist, include all relevant parts
            - If no {clause_type} clause exists, respond with "NOT FOUND"
            - Maintain original formatting and structure
            
            Contract Text:
            {contract_text}
            
            {clause_type} Clause:
            """
        )
        
        # Risk assessment prompt
        self.risk_prompt = PromptTemplate(
            input_variables=["clause_type", "clause_text", "risk_levels"],
            template="""
            Assess the legal risk level of the following {clause_type} clause.
            
            Risk Levels: {risk_levels}
            
            Consider these risk factors:
            - Potential financial exposure
            - Legal enforceability issues
            - Operational impact
            - Compliance requirements
            - Ambiguous or unclear language
            - Unfavorable terms or conditions
            
            Clause Text:
            {clause_text}
            
            Provide your assessment in this format:
            RISK_LEVEL: [one of: {risk_levels}]
            RISK_SCORE: [numerical score from 0.0 to 1.0]
            RATIONALE: [detailed explanation of the risk assessment]
            KEY_FACTORS: [list the main risk factors identified]
            RECOMMENDATIONS: [suggest improvements or mitigations]
            """
        )
        
        # Document summarization prompt
        self.summary_prompt = PromptTemplate(
            input_variables=["contract_text"],
            template="""
            Provide a comprehensive summary of this legal contract.
            
            Include:
            - Main purpose and scope of the agreement
            - Key parties and their roles
            - Primary obligations and rights
            - Important terms and conditions
            - Duration and termination provisions
            - Notable risks or concerns
            
            Keep the summary concise but comprehensive (2-4 paragraphs).
            
            Contract Text:
            {contract_text}
            
            Summary:
            """
        )
    
    def analyze_contract(self, text: str, doc_id: str) -> AnalysisResult:
        """
        Perform comprehensive analysis of a legal contract.
        
        Args:
            text: The contract text to analyze
            doc_id: Unique identifier for the document
            
        Returns:
            AnalysisResult with complete analysis
        """
        start_time = time.time()
        analysis_logger.log_analysis_start(doc_id, len(text))
        
        try:
            # Run analysis tasks in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all tasks
                classify_future = executor.submit(self._classify_contract, text)
                clauses_future = executor.submit(self._extract_clauses, text)
                summary_future = executor.submit(self._summarize_contract, text)
                
                # Wait for classification and clause extraction
                contract_type = classify_future.result()
                clauses_result = clauses_future.result()
                
                # Extract clauses and assess risks in parallel
                risks_future = executor.submit(self._assess_risks, clauses_result["clauses"])
                summary = summary_future.result()
                
                # Wait for risk assessment
                risks_result = risks_future.result()
            
            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk(risks_result["risks"])
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                contract_type, clauses_result["clauses"], risks_result["risks"]
            )
            
            processing_time = time.time() - start_time
            
            # Log results
            analysis_logger.log_clause_extraction(doc_id, len(clauses_result["clauses"]))
            analysis_logger.log_risk_assessment(doc_id, self._get_risk_distribution(risks_result["risks"]))
            analysis_logger.log_document_processed(doc_id, processing_time, True)
            
            # Performance logging
            performance_logger.log_timing(
                "contract_analysis",
                processing_time,
                doc_id=doc_id,
                text_length=len(text),
                clause_count=len(clauses_result["clauses"])
            )
            
            return AnalysisResult(
                doc_id=doc_id,
                contract_type=contract_type["classification"],
                summary=summary,
                clauses=clauses_result["clauses"],
                risks=risks_result["risks"],
                risk_rationales=risks_result["rationales"],
                overall_risk_level=overall_risk,
                confidence_score=confidence_score,
                processing_time=processing_time,
                metadata={
                    "llm_provider": llm_manager.current_provider,
                    "llm_model": llm_manager.providers[llm_manager.current_provider]["model"],
                    "classification_confidence": contract_type["confidence"],
                    "text_length": len(text),
                    "clause_count": len(clauses_result["clauses"])
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Analysis failed for {doc_id}: {str(e)}"
            logger.error(error_msg, exception=e)
            analysis_logger.log_document_processed(doc_id, processing_time, False)
            
            return AnalysisResult(
                doc_id=doc_id,
                contract_type="Unknown",
                summary="",
                clauses={},
                risks={},
                risk_rationales={},
                overall_risk_level="Unknown",
                confidence_score=0.0,
                processing_time=processing_time,
                metadata={},
                success=False,
                error_message=error_msg
            )
    
    def _classify_contract(self, text: str) -> Dict[str, Any]:
        """Classify the contract type."""
        prompt = self.classify_prompt.format(
            contract_text=text[:5000],  # Limit text for classification
            contract_types=", ".join(self.contract_types)
        )
        
        response = llm_manager.invoke(prompt)
        if response.error:
            return {"classification": "Other", "confidence": 0.0, "reasoning": "Classification failed"}
        
        # Parse response
        classification = self._extract_field(response.content, "CLASSIFICATION", "Other")
        confidence = float(self._extract_field(response.content, "CONFIDENCE", "0.0"))
        reasoning = self._extract_field(response.content, "REASONING", "No reasoning provided")
        
        return {
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def _extract_clauses(self, text: str) -> Dict[str, Any]:
        """Extract all specified clause types from the contract."""
        clauses = {}
        
        # Process clauses in parallel
        with ThreadPoolExecutor(max_workers=len(self.clause_types)) as executor:
            future_to_clause = {
                executor.submit(self._extract_single_clause, clause_type, text): clause_type
                for clause_type in self.clause_types
            }
            
            for future in as_completed(future_to_clause):
                clause_type = future_to_clause[future]
                try:
                    clause_text = future.result()
                    if clause_text and clause_text != "NOT FOUND":
                        clauses[clause_type] = clause_text
                except Exception as e:
                    logger.warning(f"Failed to extract {clause_type} clause: {e}")
        
        return {"clauses": clauses}
    
    def _extract_single_clause(self, clause_type: str, text: str) -> str:
        """Extract a single clause type from the contract."""
        prompt = self.clause_prompt.format(
            clause_type=clause_type,
            contract_text=text
        )
        
        response = llm_manager.invoke(prompt)
        if response.error:
            return ""
        
        return response.content.strip()
    
    def _assess_risks(self, clauses: Dict[str, str]) -> Dict[str, Any]:
        """Assess risks for all extracted clauses."""
        risks = {}
        rationales = {}
        
        # Process risk assessments in parallel
        with ThreadPoolExecutor(max_workers=len(clauses)) as executor:
            future_to_clause = {
                executor.submit(self._assess_single_risk, clause_type, clause_text): clause_type
                for clause_type, clause_text in clauses.items()
            }
            
            for future in as_completed(future_to_clause):
                clause_type = future_to_clause[future]
                try:
                    risk_result = future.result()
                    risks[clause_type] = risk_result["risk_level"]
                    rationales[clause_type] = risk_result["rationale"]
                except Exception as e:
                    logger.warning(f"Failed to assess risk for {clause_type}: {e}")
                    risks[clause_type] = "Unknown"
                    rationales[clause_type] = f"Risk assessment failed: {e}"
        
        return {"risks": risks, "rationales": rationales}
    
    def _assess_single_risk(self, clause_type: str, clause_text: str) -> Dict[str, str]:
        """Assess risk for a single clause."""
        prompt = self.risk_prompt.format(
            clause_type=clause_type,
            clause_text=clause_text,
            risk_levels=", ".join(self.risk_levels)
        )
        
        response = llm_manager.invoke(prompt)
        if response.error:
            return {"risk_level": "Unknown", "rationale": "Risk assessment failed"}
        
        # Parse response
        risk_level = self._extract_field(response.content, "RISK_LEVEL", "Unknown")
        rationale = self._extract_field(response.content, "RATIONALE", "No rationale provided")
        
        return {"risk_level": risk_level, "rationale": rationale}
    
    def _summarize_contract(self, text: str) -> str:
        """Generate a summary of the contract."""
        prompt = self.summary_prompt.format(contract_text=text[:8000])  # Limit text for summary
        
        response = llm_manager.invoke(prompt)
        if response.error:
            return "Summary generation failed"
        
        return response.content.strip()
    
    def _extract_field(self, text: str, field_name: str, default: str) -> str:
        """Extract a specific field from structured LLM response."""
        pattern = rf"{field_name}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else default
    
    def _calculate_overall_risk(self, risks: Dict[str, str]) -> str:
        """Calculate overall risk level based on individual clause risks."""
        if not risks:
            return "Unknown"
        
        risk_weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Unknown": 0}
        
        # Calculate weighted average
        total_weight = 0
        total_score = 0
        
        for risk_level in risks.values():
            weight = risk_weights.get(risk_level, 0)
            total_weight += 1
            total_score += weight
        
        if total_weight == 0:
            return "Unknown"
        
        avg_score = total_score / total_weight
        
        # Map back to risk level
        if avg_score >= 3.5:
            return "Critical"
        elif avg_score >= 2.5:
            return "High"
        elif avg_score >= 1.5:
            return "Medium"
        elif avg_score >= 0.5:
            return "Low"
        else:
            return "Unknown"
    
    def _calculate_confidence_score(self, contract_type: Dict, clauses: Dict, risks: Dict) -> float:
        """Calculate overall confidence score for the analysis."""
        scores = []
        
        # Classification confidence
        scores.append(contract_type.get("confidence", 0.0))
        
        # Clause extraction success rate
        clause_success_rate = len(clauses) / len(self.clause_types)
        scores.append(clause_success_rate)
        
        # Risk assessment completeness
        risk_success_rate = len([r for r in risks.values() if r != "Unknown"]) / max(len(risks), 1)
        scores.append(risk_success_rate)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_risk_distribution(self, risks: Dict[str, str]) -> Dict[str, int]:
        """Get distribution of risk levels."""
        distribution = {}
        for risk_level in risks.values():
            distribution[risk_level] = distribution.get(risk_level, 0) + 1
        return distribution


# Global agent instance
legal_agent = LegalAnalysisAgent()

# Convenience function
def analyze_document(text: str, doc_id: str) -> AnalysisResult:
    """Analyze a legal document and return the results."""
    return legal_agent.analyze_contract(text, doc_id)

@with_db_session
def analyze_and_store_document(session, text: str, doc_id: str) -> AnalysisResult:
    """Analyze document and store results in database."""
    result = analyze_document(text, doc_id)
    
    if not result.success:
        return result
    
    try:
        # Get document record
        from src.database.models import Document
        document = session.query(Document).filter(Document.doc_id == doc_id).first()
        if not document:
            logger.error(f"Document {doc_id} not found in database")
            return result
        
        # Store analysis
        analysis = Analysis(
            document_id=document.id,
            contract_type=result.contract_type,
            summary=result.summary,
            overall_risk_level=result.overall_risk_level,
            confidence_score=result.confidence_score,
            llm_provider=result.metadata.get("llm_provider"),
            llm_model=result.metadata.get("llm_model"),
            processing_metadata=result.metadata
        )
        session.add(analysis)
        session.flush()  # Get analysis ID
        
        # Store clauses and risks
        for clause_type, clause_text in result.clauses.items():
            clause = Clause(
                document_id=document.id,
                clause_type=clause_type,
                clause_text=clause_text
            )
            session.add(clause)
            session.flush()  # Get clause ID
            
            # Store risk assessment
            risk_assessment = RiskAssessment(
                document_id=document.id,
                clause_id=clause.id,
                risk_level=result.risks.get(clause_type, "Unknown"),
                rationale=result.risk_rationales.get(clause_type, "")
            )
            session.add(risk_assessment)
        
        session.commit()
        logger.info(f"Analysis results stored for document {doc_id}")
        
    except Exception as e:
        logger.error(f"Failed to store analysis results: {e}")
        session.rollback()
    
    return result
