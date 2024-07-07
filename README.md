# YouTuber - Generator Automat de Videoclipuri

## Descriere

YouTuber este o aplicație Python care generează automat videoclipuri și le încarcă pe YouTube. Utilizează inteligența artificială pentru a genera scripturi, imagini și audio, combinându-le într-un videoclip complet.

## Caracteristici

- Generare de scripturi folosind modele de limbaj (ex: GPT-4, Claude, Llama3)
- Generare de imagini folosind modele AI (ex: DALL-E 3, Stable Diffusion)
- Generare audio din text (ElevenLabs)
- Creare automată de videoclipuri
- Încărcare automată pe YouTube

## Cerințe de Sistem

- Python 3.8+
- FFmpeg (pentru procesarea video)

## Instalare

1. Clonați repository-ul:
git clone https://github.com/your-username/youtuber.git
cd youtuber

2. Creați și activați un mediu virtual:
python -m venv .venv
source .venv/bin/activate # Pe Windows folosiți: .venv\Scripts\activate

3. Instalați dependențele:
pip install -r requirements.txt
pip install -e .

4. Configurați variabilele de mediu:
Creați un fișier `.env` în directorul rădăcină și adăugați următoarele:
OPENAI_API_KEY=your_openai_api_key
SD_API_KEY=your_stability_ai_api_key
YOUTUBE_CLIENT_SECRETS_FILE=path/to/your/client_secrets.json

## Utilizare

### Interfață în linia de comandă (CLI)

Rulați comanda:

python cli/main.py --prompt "Your video topic" --length 5 --text-model gpt4 --image-model sd3


Opțiuni:
- `--prompt`: Subiectul videoclipului (obligatoriu)
- `--length`: Durata videoclipului în minute (implicit: 1)
- `--text-model`: Modelul de text de utilizat (implicit: claude)
- `--image-model`: Modelul de imagine de utilizat (implicit: sd3)
- `--verbose`: Activează output-ul detaliat

### API

Porniți serverul FastAPI:

uvicorn api.routes:app --reload

Apoi, puteți face cereri POST la `http://localhost:8000/generate_video` cu un payload JSON:

```json
{
  "prompt": "Your video topic",
  "length": 5,
  "text_model": "gpt4",
  "image_model": "sd3"
}

## Structura Proiectului

youtuber/
├── api/
│   └── routes.py
├── cli/
│   └── main.py
├── youtuber/
│   ├── __init__.py
│   ├── config.py
│   ├── script_generator.py
│   ├── image_generator.py
│   ├── audio_generator.py
│   ├── video_creator.py
│   └── uploader.py
├── .env
├── requirements.txt
└── README.md


## Contribuții
Contribuțiile sunt binevenite! Vă rugăm să deschideți un issue sau să creați un pull request pentru orice îmbunătățiri.

## Licență
[MIT]
