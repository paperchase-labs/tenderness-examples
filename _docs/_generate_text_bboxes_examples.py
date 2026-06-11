# Copyright 2026 Pavel Stepachev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import annotations

import json
import pathlib

from tenderness import (
    ColorSelector,
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    Margin,
    SolidColorSpec,
    SurfaceConfigManager,
)
from tenderness.pipelines.document import (
    DocumentBlocksConfig,
    DocumentConfig,
    DocumentRenderPipeline,
    TextBlock,
    TextBlockBBoxesResult,
    TextStyle,
)

_REPO_ROOT = pathlib.Path(__file__).parent.parent
FONTS_DIR = _REPO_ROOT / "font_groups" / "noto"
DOCS_OUTPUT_DIR = _REPO_ROOT / "_docs_output" / "_generate_text_bboxes_examples"

_colors = ColorSelector()
WHITE = SolidColorSpec(color=_colors.by_names(["white"])[0])
BLACK = SolidColorSpec(color=_colors.by_names(["black"])[0])

EXAMPLES: list[tuple[str, str, int, int]] = [
    # (slug, text, width, height)
    ("cafe_example", "café", 300, 100),
    ("latin_chinese_example", " Hello 你好 ", 300, 100),
    ("multiline_example", "This is the 1st line.\nThis is the 2nd line.", 400, 150),
    ("long_text_example", "Some XZY?!\nАБВ for sure", 300, 150),  # noqa: RUF001
]


def _generate_text_bboxes_examples(slug: str, text: str, width: int, height: int) -> None:
    out = DOCS_OUTPUT_DIR / slug
    out.mkdir(parents=True, exist_ok=True)

    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=out / "fontconfig_file",
    )

    surface_config = SurfaceConfigManager().create_image_surface_config(width=width, height=height)

    canvas_config = DocumentConfig(
        surface_config=surface_config,
        global_margin=Margin(top=10, right=10, bottom=10, left=10),
        background_spec=WHITE,
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            TextBlock(
                text=text,
                text_style=TextStyle(
                    font_description_params=FontDescriptionInterfaceParameters(
                        family="Noto Sans",
                        size_device_units=40,
                    ),
                    text_color_spec=BLACK,
                ),
            ),
        ],
    )

    pipeline = DocumentRenderPipeline()
    setup = pipeline.setup(config=canvas_config)
    rendered = pipeline.render(blocks_config=blocks_config, setup_result=setup)

    output_path = out / "output.png"
    pipeline.save_as_file(
        surface=setup.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup.stream,
    )
    print(f"  saved → {output_path}")

    block_bboxes = pipeline.get_block_bounding_boxes(setup_result=setup)
    block_json = out / "block_bboxes.json"
    block_json.write_text(json.dumps(block_bboxes.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved → {block_json}")

    text_bboxes = pipeline.get_text_bounding_boxes(rendered_blocks=rendered.rendered_blocks)
    for block_result in text_bboxes:
        if not isinstance(block_result, TextBlockBBoxesResult):
            continue
        for level_key, level_data in block_result.bboxes.to_dict().items():
            if level_data is None:
                continue
            level_name = level_key.removesuffix("_bboxes").removesuffix("_bbox")
            json_path = out / f"bboxes_{level_name}.json"
            json_path.write_text(json.dumps(level_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  saved → {json_path}")


if __name__ == "__main__":
    for slug, text, width, height in EXAMPLES:
        print(f"\n=== {slug}: {text!r} ===")
        _generate_text_bboxes_examples(slug, text, width, height)
    print("\nDone.")
