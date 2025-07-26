from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.core.scraper import ResearchScraper
from app.core.parser import ResearchParser
from app.core.exporter import ResearchExporter
import os
from datetime import datetime
import traceback

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    try:
        query = request.form.get('query')
        if not query:
            return jsonify({'error': 'No search query provided'}), 400

        scraper = ResearchScraper()
        results = scraper.search_web(query)
        
        if not results:
            return jsonify({'results': [], 'message': 'No results found'}), 200
            
        return jsonify({'results': results}), 200

    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An error occurred during search. Please try again.'}), 500

@main.route('/analyze', methods=['POST'])
def analyze():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        scraper = ResearchScraper()
        parser = ResearchParser()
        
        article = scraper.fetch_article(url)
        domain_info = scraper.get_domain_info(url)
        
        return jsonify({
            'article': article,
            'domain_info': domain_info
        }), 200

    except Exception as e:
        current_app.logger.error(f"Analysis error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An error occurred during analysis. Please try again.'}), 500

@main.route('/export', methods=['POST'])
def export():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided for export'}), 400

        export_format = data.get('format', 'docx')
        if export_format not in ['docx', 'pdf']:
            return jsonify({'error': 'Invalid export format specified'}), 400

        exporter = ResearchExporter()
        exporter.create_document()
        
        # Add content sections
        for section in data.get('sections', []):
            exporter.add_section(section['title'], section['content'])
        
        # Generate filename
        filename = f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Export the document
        if export_format == 'docx':
            exporter.export_docx(filepath)
        elif export_format == 'pdf':
            exporter.export_pdf(filepath)
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An error occurred during export. Please try again.'}), 500 