#!/bin/bash
set -e

echo "Running: song_lyrics"
python -m examples.document_pipeline.song_lyrics.song_lyrics

echo "Running: two_columns_page"
python -m examples.document_pipeline.two_columns_page.two_columns_page

echo "Running: figure_caption"
python -m examples.document_pipeline.figure_caption.figure_caption

echo "Running: multilingual"
python -m examples.document_pipeline.multilingual.multilingual

echo "Running: simple_table"
python -m examples.document_pipeline.simple_table.simple_table

echo "Running: text_bboxes"
python -m examples.document_pipeline.text_bboxes.text_bboxes

echo "Running: reaction_meme"
python -m examples.document_pipeline.reaction_meme.reaction_meme