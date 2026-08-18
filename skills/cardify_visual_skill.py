import os
import json
import urllib.parse

class CardifyVisualSkill:
    """Extract long-form content from current mobile screen and transform into 4K McKinsey Cardify Decks"""
    
    @staticmethod
    def extract_article_from_elements(elements):
        texts = []
        for eid, info in elements.items():
            label = info.get("label", "").strip()
            # Filter out tiny system icons and keep article paragraphs
            if len(label) > 10 and not any(skip in label for skip in ["WiFi", "AM", "PM", "%", "设置", "返回"]):
                texts.append(label)
        
        full_text = "\n\n".join(texts)
        return full_text

    @staticmethod
    def generate_cardify_share_url(raw_text, theme="exec"):
        clean_text = raw_text[:2000] # Safe URL length
        base_url = "https://cardifyai.lumiere-private.com/"
        params = {
            "read": theme,
            "view": "webpage",
            "prompt": clean_text
        }
        return f"{base_url}?{urllib.parse.urlencode(params)}"
