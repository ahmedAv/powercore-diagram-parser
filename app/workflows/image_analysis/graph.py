from langgraph.graph import StateGraph, END
from .state import ProcessingState
from .nodes import pdf_extractor, dimension_extractor, image_analyzer
from app.services.llm_service import LLMService
from typing import Optional


class ImageAnalysisGraph:
    def __init__(self, system_name: str = "Industrial System"):
        self.llm_service = LLMService()
        self.system_name = system_name
        self.build_graph()

    def build_graph(self):
        workflow = StateGraph(ProcessingState)

        # Add nodes
        workflow.add_node("extract_text", pdf_extractor.extract_text_from_pdf)
        workflow.add_node("extract_dimensions", self._extract_dimensions_wrapper)
        workflow.add_node("analyze_image", self._analyze_image_wrapper)

        # Define edges
        workflow.set_entry_point("extract_text")
        workflow.add_edge("extract_text", "extract_dimensions")
        workflow.add_edge("extract_dimensions", "analyze_image")
        workflow.add_edge("analyze_image", END)

        # Conditional edges for error handling
        workflow.add_conditional_edges(
            "extract_text",
            self._check_error,
            {"continue": "extract_dimensions", "error": END}
        )

        workflow.add_conditional_edges(
            "extract_dimensions",
            self._check_error,
            {"continue": "analyze_image", "error": END}
        )

        self.graph = workflow.compile()

    async def _extract_dimensions_wrapper(self, state: dict):
        return await dimension_extractor.extract_dimensions(
            state, self.llm_service
        )

    async def _analyze_image_wrapper(self, state: dict):
        image_path = state.get("image_path", "")
        return await image_analyzer.analyze_image(
            state, self.llm_service, image_path
        )

    def _check_error(self, state: dict):
        return "error" if state.get("error") else "continue"

    async def process(self, system_name, image_path: str, pdf_path: Optional[str] = None):
        initial_state = {
            "system_name": system_name,
            "pdf_file_path": pdf_path,
            "image_path": image_path
        }
        return await self.graph.ainvoke(initial_state)