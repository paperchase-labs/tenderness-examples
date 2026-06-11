import pathlib

from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImageSurfaceConfig,
    Margin,
    PDFSurfaceConfig,
    SurfaceConfigManager,
    SVGSurfaceConfig,
)
from tenderness.pipelines.document import (
    BlockBBoxesResult,
    DocumentBlocksConfig,
    DocumentConfig,
    DocumentRenderPipeline,
    TableBlockBBoxesResult,
    TextBlock,
    TextBlockBBoxesResult,
    TextStyle,
)

from examples.document_pipeline.helpers import MULTILINGUAL_SAMPLE, SOLID_WHITE, SOLID_WOOD_BARK

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/multilingual/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/multilingual")
FONTS_DIR = pathlib.Path("font_groups/noto")

surface_config_manager = SurfaceConfigManager()

IMG_SURFACE_CONFIG = surface_config_manager.create_image_surface_config(
    width=900,
    height=1280,
)
SVG_SURFACE_CONFIG = surface_config_manager.create_svg_surface_config(
    width=900,
    height=1280,
)
PDF_SURFACE_CONFIG = surface_config_manager.create_pdf_surface_config(
    width=900,
    height=1280,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_multilingual(
    surface_config: ImageSurfaceConfig | SVGSurfaceConfig | PDFSurfaceConfig,
) -> tuple[
    list[TextBlockBBoxesResult | TableBlockBBoxesResult | None],
    BlockBBoxesResult,
]:
    # 1) Setup custom fonts
    _setup_fonts()

    # 2) Define layout
    document_config = DocumentConfig(
        surface_config=surface_config,
        global_margin=Margin(top=30, right=30, bottom=30, left=30),
        background_spec=SOLID_WHITE,
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            TextBlock(
                text=MULTILINGUAL_SAMPLE,
                text_style=TextStyle(
                    font_description_params=FontDescriptionInterfaceParameters(family="Noto Sans", size=24),
                    text_color_spec=SOLID_WOOD_BARK,
                ),
            )
        ],
    )

    # 3) Render
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)
    render_result = render_pipeline.render(blocks_config=blocks_config, setup_result=setup_result)

    # 4) Extract bounding boxes
    text_bboxes = render_pipeline.get_text_bounding_boxes(
        rendered_blocks=render_result.rendered_blocks,
    )
    block_bboxes = render_pipeline.get_block_bounding_boxes(
        setup_result=setup_result,
    )

    # 5) Save
    output_path = OUTPUT_DIR / f"multilingual{surface_config.image_format.extension}"
    render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    configs: list[ImageSurfaceConfig | SVGSurfaceConfig | PDFSurfaceConfig] = [
        IMG_SURFACE_CONFIG,
        SVG_SURFACE_CONFIG,
        PDF_SURFACE_CONFIG,
    ]
    for surface_config in configs:
        text_bboxes, block_bboxes = render_multilingual(surface_config=surface_config)
        print(f"Saved → {OUTPUT_DIR}/multilingual{surface_config.image_format.extension}")
