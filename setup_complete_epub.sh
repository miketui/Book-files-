#!/bin/bash
# setup_complete_epub.sh
# Script to create and populate the complete EPUB folder structure

echo "🚀 Setting up Complete EPUB Structure for 'Curls & Contemplation'"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "book-map.yaml" ]; then
    echo "❌ Error: book-map.yaml not found. Please run this script from the Book-files- root directory."
    exit 1
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p complete/{META-INF,OEBPS/{text,styles,fonts,images}}

# Copy files with progress indicators
echo "📄 Copying XHTML files..."
cp OEBPS/text/*.xhtml complete/OEBPS/text/
echo "   ✅ Copied $(ls OEBPS/text/*.xhtml | wc -l) XHTML files"

echo "🎨 Copying stylesheets..."
cp OEBPS/styles/*.css complete/OEBPS/styles/
echo "   ✅ Copied $(ls OEBPS/styles/*.css | wc -l) CSS files"

echo "🔤 Copying fonts..."
cp OEBPS/fonts/*.woff2 complete/OEBPS/fonts/
echo "   ✅ Copied $(ls OEBPS/fonts/*.woff2 | wc -l) font files"

echo "🖼️  Copying images..."
cp OEBPS/images/*.{JPEG,PNG} complete/OEBPS/images/ 2>/dev/null
echo "   ✅ Copied $(ls OEBPS/images/*.{JPEG,PNG} 2>/dev/null | wc -l) image files"

echo "⚙️  Copying configuration files..."
cp OEBPS/content.opf complete/OEBPS/
cp META-INF/container.xml complete/META-INF/
cp mimetype complete/
cp book-map.yaml complete/
echo "   ✅ Copied 4 configuration files"

# Verify structure
echo ""
echo "📊 Complete folder summary:"
echo "   Directory structure: $(find complete -type d | wc -l) directories"
echo "   Total files: $(find complete -type f | wc -l) files"
echo ""

# Show structure
echo "🌳 Complete folder structure:"
echo "================================"
if command -v tree >/dev/null 2>&1; then
    cd complete && tree -a && cd ..
else
    find complete -type f | sort
fi

echo ""
echo "✅ Complete EPUB structure ready!"
echo "📁 Location: $(pwd)/complete/"
echo ""
echo "🔧 Next steps:"
echo "   1. Navigate to complete folder: cd complete/"
echo "   2. Create EPUB: zip -r ../curls-and-contemplation-complete.epub mimetype META-INF/ OEBPS/"
echo "   3. Validate: java -jar ../epubcheck-4.2.6/epubcheck.jar ../curls-and-contemplation-complete.epub"
echo ""
echo "📖 For detailed documentation, see: COMPLETE_EPUB_DIRECTORY_GUIDE.md"