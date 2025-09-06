#!/usr/bin/env python3
"""
Add sample God facts to test the system
"""

import sys
sys.path.append('.')

from app import app
from models import db, GodFact

def add_sample_facts():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Sample facts that prove God is real
        sample_facts = [
            {
                'title': 'The Fine-Tuned Universe Constants',
                'content': '''The fundamental constants of physics are precisely fine-tuned for life to exist. The cosmological constant, if altered by even 1 part in 10^120, would prevent the formation of stars and galaxies. The strong nuclear force, if changed by just 2%, would prevent the formation of protons and neutrons. These precise values point to an intelligent Designer who set the parameters of the universe exactly right for life to flourish.

Scientists like Sir Martin Rees have identified at least six dimensionless physical constants that must be precisely calibrated for a universe capable of supporting complex life. The probability of this happening by chance is astronomically small, leading many physicists to conclude that the universe was designed by an intelligent Creator.''',
                'category': 'science',
                'source': 'Martin Rees, "Just Six Numbers: The Deep Forces That Shape the Universe"',
                'status': 'published'
            },
            {
                'title': 'The Resurrection of Jesus Christ - Historical Evidence',
                'content': '''Historical scholars, including non-Christians, acknowledge several key facts about Jesus\' crucifixion and resurrection:

1. Jesus of Nazareth was crucified by Roman authorities around 30-33 AD
2. His tomb was found empty by women followers on the third day
3. Multiple groups of people claimed to have seen Jesus alive after his crucifixion
4. The disciples were transformed from fearful followers to bold preachers, willing to die for their testimony
5. The Christian movement exploded in the very city where Jesus was publicly executed

Even skeptical historians like Gerd Lüdemann acknowledge these core facts. The resurrection hypothesis best explains this historical data, providing powerful evidence for the divine nature of Jesus Christ.''',
                'category': 'history',
                'source': 'Gary Habermas, "The Case for the Resurrection of Jesus"',
                'status': 'published'
            },
            {
                'title': 'DNA: The Digital Code of Life',
                'content': '''DNA contains a sophisticated digital information system more complex than any computer code ever written by humans. Each cell contains 3.2 billion precisely sequenced chemical letters that store the complete instructions for building and maintaining a living organism.

Information theory tells us that information always requires an intelligent source. We have never observed complex, specified information arising spontaneously from random processes. The intricate programming in DNA, with its error-correction systems and information storage capacity, points unmistakably to an intelligent Programmer - God.

As Francis Crick, co-discoverer of DNA structure, admitted: "An honest man, armed with all the knowledge available to us now, could only state that in some sense, the origin of life appears at the moment to be almost a miracle."''',
                'category': 'science',
                'source': 'Stephen Meyer, "Signature in the Cell: DNA and the Evidence for Intelligent Design"',
                'status': 'published'
            },
            {
                'title': 'Biblical Prophecy: Israel\'s Restoration',
                'content': '''In 586 BC, the prophet Ezekiel made remarkable prophecies about Israel\'s future restoration when the nation was destroyed and scattered. He predicted:

• Israel would be regathered from all nations (Ezekiel 36:24)
• The land would become fruitful again after being desolate (Ezekiel 36:34-35)
• Jerusalem would be rebuilt and inhabited (Ezekiel 36:10)
• Israel would become a nation in one day (Isaiah 66:8)

Against all historical precedent, these prophecies were fulfilled precisely:
- May 14, 1948: Israel became a nation in one day by UN vote
- Jewish people returned from over 100 countries
- Israel transformed desert lands into agricultural abundance
- Jerusalem was rebuilt and became Israel\'s capital again

No other ancient nation has been restored after such complete destruction and diaspora. This miraculous restoration demonstrates God\'s faithfulness to His prophetic word.''',
                'category': 'prophecy',
                'source': 'Tim LaHaye & Ed Hindson, "The Popular Encyclopedia of Bible Prophecy"',
                'status': 'published'
            },
            {
                'title': 'The Cambrian Explosion: Life\'s Sudden Appearance',
                'content': '''The Cambrian period (about 540 million years ago) witnessed what Darwin called an "abrupt" appearance of complex life forms in the fossil record. In a relatively short geological time span, nearly all major animal groups (phyla) appeared suddenly with sophisticated body plans, organs, and biological systems.

This "Cambrian Explosion" poses major challenges to gradual evolutionary theory:

• Complex creatures appear without evolutionary predecessors
• Advanced features like eyes, nervous systems, and digestive tracts emerge fully formed
• The speed of appearance contradicts slow, gradual change
• Information required for these complex body plans exceeds what random mutations can generate

Even evolutionary biologist James Valentine admits: "The Cambrian explosion was the most remarkable and puzzling event in the history of life." This sudden burst of complex, designed life points to a Creator who brought forth life according to His plan.''',
                'category': 'creation',
                'source': 'Stephen Meyer, "Darwin\'s Doubt: The Explosive Origin of Animal Life"',
                'status': 'published'
            },
            {
                'title': 'Miraculous Healing: The Case of Duane Miller',
                'content': '''In 1990, Duane Miller, a Baptist preacher, lost his voice due to a viral infection that damaged his vocal cords. For three years, he could only whisper and was medically declared permanently disabled by multiple doctors.

On January 17, 1993, while teaching a Sunday school class on divine healing, Miller\'s voice was miraculously restored instantly during the lesson. The entire event was recorded on audio tape, capturing the exact moment his voice returned to normal.

Medical examination confirmed:
• His vocal cords were completely healed
• Scar tissue had vanished
• Voice quality was fully restored
• No medical explanation could account for the healing

This documented miracle demonstrates God\'s power to heal and His continued intervention in human lives. Thousands of similar documented healings occur worldwide, showing that the God of miracles is still active today.''',
                'category': 'miracles',
                'source': 'Documented case study and medical records',
                'status': 'published'
            }
        ]
        
        # Add sample facts
        added_count = 0
        for fact_data in sample_facts:
            # Check if fact already exists
            existing = GodFact.query.filter_by(title=fact_data['title']).first()
            if not existing:
                fact = GodFact(**fact_data)
                db.session.add(fact)
                added_count += 1
        
        db.session.commit()
        print(f"Added {added_count} sample God facts to the database")
        print(f"Total facts in database: {GodFact.query.count()}")

if __name__ == "__main__":
    add_sample_facts()