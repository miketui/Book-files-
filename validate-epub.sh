#!/bin/bash

# EPUB validation script for Book-files project
# Sets up Java environment and runs epubcheck

# Set Java environment
export JAVA_HOME=/Users/yurielyoung/Book-files-/jdk-11.0.2.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH

# Default EPUB file
EPUB_FILE=${1:-"curls-and-contemplation.epub"}

echo "Validating EPUB: $EPUB_FILE"
echo "Java version: $(java -version 2>&1 | head -1)"
echo "EPUBCheck version:"

# Run epubcheck
java -jar epubcheck-4.2.6/epubcheck.jar "$EPUB_FILE"