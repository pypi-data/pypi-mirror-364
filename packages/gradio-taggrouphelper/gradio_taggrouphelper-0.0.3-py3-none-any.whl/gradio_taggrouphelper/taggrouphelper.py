from __future__ import annotations
from gradio.components.base import Component
from typing import Any, Dict, List

class TagGroupHelper(Component):
    """
    A custom component that displays groups of clickable tags to help build prompts.
    When a tag is clicked, it's appended to a target Textbox component.
    This component does not have a submittable value itself.
    """
    EVENTS = []

    def __init__(
        self,
        value: Dict[str, List[str]] | None = None,
        *,
        height: int | None = None,
        width: int | None = None,
        label: str | None = None,
        font_size_scale: int = 100,
        every: float | None = None,
        show_label: bool | None = None,
        container: bool = True,        
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        target_textbox_id: str | None = None,
        separator: str = ", ",
        visible: bool = True,
        elem_id: str | None = None,        
        elem_classes: list[str] | str | None = None,
        
        **kwargs,
    ):
        """
        Initializes the TagGroupHelper component.

        Parameters:
            value: A dictionary where keys are group names and values are lists of tags.
            height: The height of the component container in pixels.
            width: The width of the component container in pixels.
            label: The label for this component, displayed above the groups.
            font_size_scale: A percentage to scale the font size of group headers and tags. Defaults to 100.
            every: If `value` is a callable, run the function 'every' seconds while the client connection is open.
            show_label: If False, the label is not displayed.
            container: If False, the component will not be wrapped in a container.
            scale: The relative size of the component compared to others in a `gr.Row` or `gr.Column`.                        
            min_width: The minimum width of the component in pixels.
            interactive: if True, will be rendered as an selectable component; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            target_textbox_id: The `elem_id` of the `gr.Textbox` component to target. Required.
            separator: The string to use as a separator between tags. Defaults to ", ". Can be set to " " for space separation.
            visible: If False, the component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM.            
            elem_classes: An optional list of strings to assign as CSS classes to the component.
        """
        if target_textbox_id is None:
            raise ValueError("The 'target_textbox_id' parameter is required for the TagGroupHelper component.")

        self.target_textbox_id = target_textbox_id
        self.separator = separator
        self.width = width
        self.height = height
        self.font_size_scale = font_size_scale
        
        # Call the parent constructor with all the arguments it understands.
        super().__init__(
            label=label,
            visible=visible,
            elem_id=elem_id,
            value=value,            
            every=every,
            show_label=show_label,  
            interactive=interactive,
            scale=scale,
            min_width=min_width,
            container=container,
            elem_classes=elem_classes,
            **kwargs,
        )
   
    def preprocess(self, payload: Any) -> Any:
        """This component does not process input from the user, so this is a no-op."""
        return None

    def postprocess(self, value: Dict[str, List[str]] | None) -> Dict[str, List[str]] | None:
        """Passes the tag group dictionary (received as 'value') to the frontend."""
        if value is None:
            return {}
        return value

    def api_info(self) -> Dict[str, Any]:
        """The API info for the component."""
        return {"type": "object", "description": "A dictionary of string-to-string-list mappings for tag groups."}

    def example_payload(self) -> Any:
        """Returns an example of the data that this component expects as its value."""
        return {
            "Quality": ["best quality", "high resolution"],
            "Style": ["anime", "photorealistic"],
            "Negative": ["blurry", "noisy"]
        }