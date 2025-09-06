#!/usr/bin/env python3
"""
Simple script to run the Paleo Hebrew app
"""

from app import app

if __name__ == '__main__':
    print('Starting Paleo Hebrew Bible app on http://localhost:5002')
    app.run(host='127.0.0.1', port=5002, debug=True)