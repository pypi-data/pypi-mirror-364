KEYWORD_ANALYSIS_PROMPT = """
Przeanalizuj poniższy tekst pod kątem słowa kluczowego: {keyword}

Tekst do analizy:
{text}

Proszę o:
1. Identyfikację głównych tematów i podtematów
2. Znalezienie powiązanych słów kluczowych
3. Określenie intencji użytkownika
4. Analizę konkurencyjności
5. Sugestie dotyczące optymalizacji

Format odpowiedzi:
{
    "main_topics": ["temat1", "temat2", ...],
    "related_keywords": ["słowo1", "słowo2", ...],
    "user_intent": "opis intencji",
    "competition_level": "niski/średni/wysoki",
    "optimization_suggestions": ["sugestia1", "sugestia2", ...]
}
""" 