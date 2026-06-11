import pathlib

import cairo
from PIL import Image
from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImageSurfaceConfig,
    ImageTextBoundingBoxDrawer,
    Margin,
    SurfaceConfigManager,
    TextDrawConfig,
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

from examples.document_pipeline.helpers import SOLID_WHITE, SOLID_WOOD_BARK

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/text_bboxes/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/text_bboxes")
FONTS_DIR = pathlib.Path("font_groups/noto")

SAMPLE_TEXT = (
    "café résumé naïve\n"  # CHAR vs CLUSTER: e+U+0301 are 2 chars but render as 1 cluster (é)
    "Hello مرحبا 你好 Привет\n"  # RUN BOUNDARY: each script is a separate run; Arabic also flips direction (RTL)
    "👨‍👩‍👧‍👦 👩‍🚀 🐻‍❄️ 🧑🏽‍💻\n"  # CLUSTER: ZWJ sequences — 4–7 code points each, but always 1 indivisible cluster  # noqa: RUF003
    "The quick brown fox jumps over the lazy dog"  # LINE BREAK: long enough to wrap, producing multiple layout lines
)

surface_config_manager = SurfaceConfigManager()

IMG_SURFACE_CONFIG = surface_config_manager.create_image_surface_config(
    width=1280,
    height=1280,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_text_bboxes(
    surface_config: ImageSurfaceConfig,
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
                text=SAMPLE_TEXT,
                text_style=TextStyle(
                    font_description_params=FontDescriptionInterfaceParameters(family="Noto Sans", size=40),
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
    output_path = OUTPUT_DIR / f"text_bboxes{surface_config.image_format.extension}"
    saved_file_path = render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    # 6) Draw bounding boxes (image surfaces only)
    if isinstance(setup_result.surface, cairo.ImageSurface):
        draw_config = TextDrawConfig(draw_labels=False)
        bbox_drawer = ImageTextBoundingBoxDrawer()
        for i, bbox_collection in enumerate(text_bboxes):
            if isinstance(bbox_collection, TextBlockBBoxesResult):
                source_image = Image.open(saved_file_path)
                for level, annotated_image in bbox_drawer.draw_per_level(
                    image=source_image,
                    text_bounding_boxes=bbox_collection.bboxes,
                    config=draw_config,
                ):
                    annotated_path = (
                        OUTPUT_DIR
                        / f"text_bboxes_{i}_annotated_{level.name.lower()}{surface_config.image_format.extension}"
                    )
                    annotated_image.save(annotated_path)
                    print(f"Saved → {annotated_path}")

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    for surface_config in [IMG_SURFACE_CONFIG]:
        text_bboxes, block_bboxes = render_text_bboxes(surface_config)
        print(f"Saved → {OUTPUT_DIR}/text_bboxes{surface_config.image_format.extension}")
