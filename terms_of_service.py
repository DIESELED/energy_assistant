"""
Nutzungsbedingungen für den Enerlytic Bot
"""

TERMS_OF_SERVICE = """
📋 Nutzungsbedingungen für den Enerlytic Bot

1️⃣ Beschreibung des Dienstes
• Der Enerlytic Bot ist ein KI-gestützter Assistent für Energiespartipps
• Der Bot bietet personalisierte Empfehlungen zum Energiesparen
• Wir können Produktempfehlungen über Affiliate-Links bereitstellen
• Der Service nutzt modernste KI-Technologie (OpenAI GPT-4) für die Kommunikation

2️⃣ Haftungsausschluss
• Wir übernehmen keine Garantie für tatsächliche Energieeinsparungen
• Die Empfehlungen des Bots ersetzen keine professionelle Energieberatung
• Alle Tipps sollten vor der Umsetzung auf ihre individuelle Anwendbarkeit geprüft werden
• Wir haften nicht für Schäden, die aus der Nutzung der Empfehlungen entstehen

3️⃣ Nutzungsbeschränkungen
• Die Nutzung des Bots ist ausschließlich für private Zwecke gestattet
• Nicht erlaubt sind:
  - Automatisierte Massenabfragen
  - Missbrauch oder Manipulation des Bots
  - Weiterverkauf oder kommerzielle Nutzung der Antworten
  - Verbreitung illegaler oder schädlicher Inhalte

4️⃣ Kosten und Nutzung
• Die grundlegende Nutzung des Bots ist kostenlos
• Wir nutzen kostenpflichtige KI-Modelle (OpenAI)
• Wir behalten uns vor, zukünftig Premium-Funktionen einzuführen

5️⃣ Affiliate-Links
• Der Bot kann Produktempfehlungen mit Affiliate-Links aussprechen
• Bei Käufen über diese Links erhalten wir möglicherweise eine Provision
• Dies hat keine Auswirkung auf den Kaufpreis für Sie
• Affiliate-Links werden immer als solche gekennzeichnet

6️⃣ Datenschutz
• Für Informationen zur Datenverarbeitung siehe unsere Datenschutzerklärung (/privacy)
• Wir speichern nur die für den Betrieb notwendigen Daten
• Ihre Daten werden nicht ohne Ihre Zustimmung an Dritte weitergegeben

7️⃣ Änderungen der Nutzungsbedingungen
• Wir behalten uns vor, diese Nutzungsbedingungen jederzeit zu ändern
• Über wesentliche Änderungen werden Sie informiert
• Die weitere Nutzung nach Änderungen gilt als Zustimmung

Bei Fragen zu den Nutzungsbedingungen kontaktieren Sie uns bitte unter:
📧 terms@enerlytic.de
"""

def get_terms_of_service() -> str:
    """
    Gibt die Nutzungsbedingungen zurück.
    
    Returns:
        str: Die formatierten Nutzungsbedingungen
    """
    return TERMS_OF_SERVICE 