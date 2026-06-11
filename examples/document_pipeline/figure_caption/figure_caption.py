import pathlib

from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImageSurfaceConfig,
    LayoutInterfaceParameters,
    MinimalFlexBoxTemplates,
    SurfaceConfigManager,
)
from tenderness.pipelines.document import (
    BlockBBoxesResult,
    DocumentBlocksConfig,
    DocumentConfig,
    DocumentRenderPipeline,
    ImageBlock,
    TableBlockBBoxesResult,
    TextBlock,
    TextBlockBBoxesResult,
    TextStyle,
)

from examples.document_pipeline.helpers import (
    SOLID_BLACK,
    SOLID_WHITE,
)

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/figure_caption/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/figure_caption")
FONTS_DIR = pathlib.Path("font_groups/bruno_ace")
IMAGE_PATH = pathlib.Path("images/ghost_1278_765.png")
CAPTION_TEXT = (
    "Figure 1: The cyborg and the fully cybernetic human are watching you, "
    "wondering why your frontier lab still trains models on nothing but plain Unicode text."
)

surface_config_manager = SurfaceConfigManager()

IMG_SURFACE_CONFIG = surface_config_manager.create_image_surface_config(
    width=1400,
    height=900,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_figure_caption(
    surface_config: ImageSurfaceConfig,
) -> tuple[
    list[TextBlockBBoxesResult | TableBlockBBoxesResult | None],
    BlockBBoxesResult,
]:
    # 1) Setup custom fonts
    _setup_fonts()

    # 2) Define layout
    block_spec = MinimalFlexBoxTemplates.figure_caption_templates.stack_figure_caption(
        caption_height=200,
        gap=20,
        caption_on_top=False,
    )
    document_config = DocumentConfig(
        surface_config=surface_config,
        block_spec=block_spec,
        background_spec=SOLID_WHITE,
    )

    # 3) Build blocks
    caption_style = TextStyle(
        font_description_params=FontDescriptionInterfaceParameters(family="Bruno Ace SC", size=28),
        text_color_spec=SOLID_BLACK,
        layout_interface_params=LayoutInterfaceParameters(alignment="center"),
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            ImageBlock(block_name="image", path_to_image=IMAGE_PATH),
            TextBlock(block_name="caption", text=CAPTION_TEXT, text_style=caption_style),
        ],
    )

    # 4) Render
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)
    render_result = render_pipeline.render(blocks_config=blocks_config, setup_result=setup_result)

    # 5) Extract bounding boxes
    text_bboxes = render_pipeline.get_text_bounding_boxes(
        rendered_blocks=render_result.rendered_blocks,
    )
    block_bboxes = render_pipeline.get_block_bounding_boxes(
        setup_result=setup_result,
    )

    # 6) Save
    output_path = OUTPUT_DIR / f"figure_caption{surface_config.image_format.extension}"
    render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    for surface_config in [IMG_SURFACE_CONFIG]:
        text_bboxes, block_bboxes = render_figure_caption(surface_config)
        print(f"Saved → {OUTPUT_DIR}/figure_caption{surface_config.image_format.extension}")
