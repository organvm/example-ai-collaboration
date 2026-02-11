# Example AI Collaboration

[![ORGAN-II: Poiesis](https://img.shields.io/badge/ORGAN--II-Poiesis-6a1b9a?style=flat-square)](https://github.com/organvm-ii-poiesis)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active--development-yellow?style=flat-square)]()

> A framework for human-AI collaborative art-making -- documenting the "AI-conductor" model as artistic methodology, exploring authorship, creative agency, and the aesthetics of algorithmic partnership through concrete examples in visual, sonic, and narrative media.

[Artistic Purpose](#artistic-purpose) | [Conceptual Approach](#conceptual-approach) | [Technical Overview](#technical-overview) | [Installation](#installation) | [Quick Start](#quick-start) | [Working Examples](#working-examples) | [Theory Implemented](#theory-implemented) | [Portfolio & Exhibition](#portfolio--exhibition) | [Related Work](#related-work) | [Contributing](#contributing) | [License & Author](#license--author)

---

## Artistic Purpose

The question of 2026 is not whether AI can make art. It can generate images that win photography competitions, compose music that audiences cannot distinguish from human composition, and write prose that passes editorial review. The question is what happens when a human artist works with AI as a creative partner rather than a tool -- when the human does not prompt the machine to produce a finished artifact but enters into an iterative dialogue where each party's output becomes the other's input, where the final work is authored by neither alone, where the creative process itself becomes the subject of the art.

Example AI Collaboration is a framework for this practice. It documents, implements, and theorizes the "AI-conductor" model: a methodology where AI systems generate volume -- visual compositions, musical phrases, narrative fragments, code -- and human artists curate, sequence, refine, and recontextualize that output into finished works. The conductor metaphor is precise: an orchestral conductor does not play the instruments, but the performance is unmistakably shaped by their interpretation. The AI is the orchestra -- capable of producing an enormous range of sonic (or visual, or textual) material -- and the human is the conductor, shaping that material into a coherent artistic statement through selection, emphasis, timing, and rejection.

This repository is not a wrapper around an API. It is a documented artistic practice. It contains the methodological framework (how to structure a human-AI collaborative session), the technical infrastructure (pipelines for generating, filtering, curating, and composing AI-generated material across visual, audio, and text modalities), the theoretical apparatus (how to think about authorship, agency, and aesthetics in the context of human-AI collaboration), and concrete examples of finished works produced through the methodology. It exists because the discourse around AI art in 2026 is still dominated by two positions -- "AI is just a tool" and "AI is replacing artists" -- and both positions are wrong. The interesting space is the space between them, where human and machine are genuinely collaborating, and the resulting work belongs to neither and both.

The project is the most self-referential component of the eight-organ system. The entire organvm architecture operates on the AI-conductor model: AI generates documentation, READMEs, essays, code scaffolds, and the human author curates, refines, and positions the output. Example AI Collaboration takes this operational methodology and elevates it to artistic practice. It asks: if the way we build this system is itself a form of human-AI collaboration, can we treat the methodology as art? Can the process be the portfolio piece?

---

## Conceptual Approach

### The AI-Conductor Model

The AI-conductor model has three phases, each with a distinct relationship between human and machine:

**Phase 1: Generation**
The AI produces material in response to structured prompts. The prompts are not "make me a painting" -- they are compositional instructions: "generate 50 variations of a color palette using these three anchor colors with increasing chromatic tension," or "compose 20 four-bar phrases in Dorian mode with syncopation values between 0.3 and 0.7," or "write 30 opening sentences for an essay about the phenomenology of waiting, each using a different rhetorical strategy." The generation phase prioritizes quantity and variation over quality. The human's role in this phase is to design the prompt space -- to define the parameters within which the AI explores -- not to evaluate individual outputs.

**Phase 2: Curation**
The human reviews the generated material and selects, rejects, groups, and sequences it. This is the phase where artistic judgment operates. A curator at a gallery does not make the art -- they select and arrange it, and the selection and arrangement constitute a creative act. The AI-conductor model makes this curatorial act explicit and central. The human might select 8 of 50 palettes, arrange them in a sequence that creates a chromatic narrative, and identify gaps where additional generation is needed. The human might select 5 of 20 musical phrases, arrange them into a structure (ABACB), and request variations of the B phrase with reduced rhythmic density. The curation phase is iterative: selections inform new generation prompts, which produce new material for further curation.

**Phase 3: Composition**
The human assembles the curated material into a finished work, adding elements that AI cannot produce: contextual meaning, cultural reference, emotional arc, structural coherence at the macro level, and the specific intentionality that makes a work of art more than a collection of competent fragments. Composition may involve manual editing (painting over AI-generated images, re-orchestrating AI-generated musical phrases, rewriting AI-generated sentences) or it may involve purely structural decisions (sequencing, timing, spatial arrangement, juxtaposition). The composition phase is where authorship crystallizes: the finished work is not what the AI generated, and it is not what the human would have made alone. It is the product of a dialogue.

### Authorship as Spectrum

The framework rejects the binary question "who is the author?" in favor of a continuous authorship spectrum with four named positions:

| Position | Human Role | AI Role | Authorship Attribution |
|----------|-----------|---------|----------------------|
| **Promptcraft** | Designs prompt, selects best output | Generates all material | "Created with AI" |
| **Curation** | Selects, sequences, arranges | Generates material pool | "Curated from AI-generated material" |
| **Dialogue** | Iterative refinement, conceptual direction | Generates, responds to feedback | "Human-AI collaboration" |
| **Augmentation** | Creates primary work, uses AI for specific tasks | Assists with defined subtasks | "Created by [human], AI-assisted" |

Most AI art in 2026 occupies the Promptcraft position. The AI-conductor model operates primarily in the Dialogue position, with excursions into Curation and Augmentation depending on the specific task. The framework does not prescribe where on the spectrum an artist should work -- it makes the spectrum visible so that artists can make deliberate choices about their relationship to the AI and communicate those choices to audiences.

### The Aesthetics of Algorithmic Partnership

There is an aesthetic quality specific to human-AI collaborative work that is distinct from both human-made art and AI-generated art. It emerges from the tension between the AI's capacity for variation (it can produce more material than any human could evaluate) and the human's capacity for meaning (it can contextualize material in ways no current AI system can). The resulting works often have a quality of productive strangeness: they contain elements that a human would not have thought of (because the AI explored a region of the parameter space the human would have ignored) but they are arranged with a coherence that the AI would not have produced (because the human imposed narrative, emotional, or structural logic on the raw material).

This aesthetic is not a compromise or a lowest common denominator. It is a genuine third thing -- neither human expression nor machine generation, but a creative dynamic that requires both parties and cannot be reduced to either. The framework documents and cultivates this aesthetic through worked examples across three media (visual, audio, text) and provides vocabulary for discussing it in exhibition contexts, grant applications, and critical writing.

---

## Technical Overview

### Repository Structure

```
example-ai-collaboration/
├── methodology/
│   ├── ai-conductor-model.md     # The three-phase methodology
│   ├── authorship-spectrum.md    # Framework for attribution
│   ├── session-structure.md      # How to run a collaborative session
│   ├── prompt-design.md          # Principles of generative prompt craft
│   └── evaluation-criteria.md   # How to assess collaborative output
├── pipelines/
│   ├── visual/
│   │   ├── generation.py         # Image generation pipeline
│   │   ├── curation.py          # Visual similarity + filtering
│   │   ├── composition.py       # Layout and sequencing tools
│   │   └── style-transfer.py    # Cross-style blending
│   ├── audio/
│   │   ├── generation.py         # Music generation pipeline
│   │   ├── curation.py          # Audio feature analysis + filtering
│   │   ├── composition.py       # Arrangement and mixing tools
│   │   └── synthesis.py         # SuperCollider integration
│   ├── text/
│   │   ├── generation.py         # Text generation pipeline
│   │   ├── curation.py          # Semantic clustering + filtering
│   │   ├── composition.py       # Narrative sequencing
│   │   └── voice-alignment.py   # Style consistency tools
│   └── multimodal/
│       ├── cross-modal.py        # Image-to-sound, text-to-image bridges
│       └── synchronization.py   # Temporal alignment across modalities
├── examples/
│   ├── 01-chromatic-dialogues/   # Visual: AI-generated palettes, human composition
│   ├── 02-emergent-scores/       # Audio: AI phrases, human arrangement
│   ├── 03-ghost-narratives/      # Text: AI fragments, human narrative structure
│   ├── 04-synaesthetic-bridge/   # Multimodal: image-to-sound-to-text
│   └── 05-meta-portrait/        # Self-referential: the methodology as artwork
├── exhibition/
│   ├── artist-statements/        # Template and examples for exhibition contexts
│   ├── wall-text/               # Gallery wall text explaining the methodology
│   ├── process-documentation/   # How to document collaborative process for display
│   └── audience-engagement/     # Interactive components for exhibition visitors
├── analysis/
│   ├── attribution-tracker.py    # Log human vs AI contributions per work
│   ├── process-visualizer.py    # Visualize the generation-curation-composition flow
│   └── aesthetic-metrics.py     # Quantitative measures of collaborative output
├── docs/
│   ├── theory.md                # Theoretical foundations
│   ├── ethics.md                # Ethical considerations in AI art
│   ├── pedagogy.md              # Teaching human-AI collaboration
│   └── critical-responses.md   # Engaging with criticism of AI art
├── scripts/
│   ├── setup-environment.sh     # Configure API keys + local models
│   ├── run-session.py           # Interactive collaborative session runner
│   └── export-portfolio.py      # Generate portfolio-ready documentation
└── requirements.txt
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Visual Generation | Stable Diffusion XL, DALL-E 3 | Image generation with fine control |
| Audio Generation | MusicGen, AudioCraft | Music and sound generation |
| Text Generation | Claude, GPT-4, local LLMs | Text generation with style control |
| Visual Curation | CLIP embeddings, UMAP | Similarity analysis + clustering |
| Audio Curation | Librosa, Essentia | Audio feature extraction + analysis |
| Text Curation | Sentence transformers | Semantic clustering + filtering |
| Cross-Modal | CLAP (audio-text), CLIP (image-text) | Modality bridging |
| Process Logging | Python, SQLite | Attribution tracking |
| Exhibition Tools | Three.js, Web Audio API | Interactive exhibition components |
| Runtime | Python 3.11+ | Primary pipeline language |
| Audio Synthesis | SuperCollider 3.13+ via OSC | Real-time audio rendering |

### Pipeline Architecture

Each modality (visual, audio, text) follows the same three-phase pipeline, implemented as composable Python functions:

```python
# Simplified pipeline structure
from pipelines.visual import generation, curation, composition

# Phase 1: Generate
candidates = generation.generate(
    prompt_template="abstract composition with {color} dominance and {texture} texture",
    parameter_space={
        "color": ["cerulean", "ochre", "viridian", "magenta", "raw umber"],
        "texture": ["smooth", "granular", "fibrous", "crystalline"],
    },
    n_per_combination=5,  # 5 x 5 x 4 = 100 candidates
    model="sdxl-1.0",
    seed_range=(0, 999),
)

# Phase 2: Curate
selected = curation.curate(
    candidates=candidates,
    method="clip_similarity",
    reference_images=["references/agnes-martin-01.jpg", "references/hilma-af-klint-03.jpg"],
    threshold=0.65,
    max_select=15,
    human_review=True,  # Opens interactive review interface
)

# Phase 3: Compose
artwork = composition.compose(
    selected=selected,
    layout="grid_3x5",
    color_harmonization=True,
    export_format="tiff",
    resolution=4096,
)
```

The `human_review=True` flag in the curation phase opens an interactive browser-based interface where the human artist can accept, reject, flag for revision, or annotate each candidate. Every human decision is logged with a timestamp and rationale field, creating a complete process record that can be displayed as part of the finished work's exhibition documentation.

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js >= 18.0.0 (for exhibition tools)
- CUDA-capable GPU (recommended for local model inference)
- API keys for cloud generation services (optional -- local models supported)

### Setup

```bash
# Clone the repository
git clone https://github.com/organvm-ii-poiesis/example-ai-collaboration.git
cd example-ai-collaboration

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (or configure local model paths)

# Verify installation
python -m pytest tests/ -v

# Run the interactive session interface
python scripts/run-session.py
```

### Local Model Configuration

For artists who prefer to work entirely offline or who want full control over the generative models:

```bash
# Download and configure local Stable Diffusion
python scripts/setup-local-models.py --visual sdxl

# Download and configure local audio generation
python scripts/setup-local-models.py --audio musicgen-medium

# Download and configure local text generation
python scripts/setup-local-models.py --text llama-3-8b

# Verify local model setup
python scripts/run-session.py --local-only
```

---

## Quick Start

### 15-Minute Collaborative Session

```bash
# Start an interactive visual collaboration session
python scripts/run-session.py --modality visual --duration 15m

# The session runner will:
# 1. Present a prompt design interface
# 2. Generate 50 visual candidates
# 3. Open the curation interface for human review
# 4. Compose selected images into a layout
# 5. Export the result + process documentation
```

### Minimal Script Example

```python
# quick-start.py
# A minimal human-AI collaboration in 30 lines

from pipelines.visual import generation, curation
from pipelines.text import generation as text_gen

# Generate visual candidates
images = generation.generate(
    prompt_template="landscape at {time_of_day}, {atmosphere}, painterly style",
    parameter_space={
        "time_of_day": ["dawn", "noon", "dusk", "midnight"],
        "atmosphere": ["serene", "turbulent", "liminal", "ecstatic"],
    },
    n_per_combination=3,
)

# Curate: human selects favorites
selected = curation.curate(
    candidates=images,
    method="human_only",  # No algorithmic pre-filtering
    max_select=5,
)

# Generate ekphrastic text for each selected image
for img in selected:
    poem = text_gen.generate(
        prompt=f"Write a four-line poem responding to this image: {img.description}",
        n_candidates=10,
    )
    # Human selects the best poem for each image
    chosen_poem = text_gen.curate(poem, method="human_only", max_select=1)
    img.attach_text(chosen_poem[0])

# Export as a visual-textual diptych series
selected.export("output/diptych-series/", format="pdf")
```

This script produces a series of image-text diptychs: AI generates both the images and the poems, and the human curates both, creating a work that is neither purely visual nor purely literary but a dialogue between the two. The human's artistic contribution is entirely curatorial -- selecting, pairing, sequencing -- and the result is unmistakably authored by the human's taste and judgment even though every individual element was generated by AI.

---

## Working Examples

### Example 1: Chromatic Dialogues

A series of 12 large-format prints produced through iterative visual collaboration. The process began with five reference images (works by Agnes Martin, Hilma af Klint, and Bridget Riley) that established an aesthetic direction: geometric abstraction with chromatic subtlety. The AI generated 500 variations across a parameter space defined by dominant color, geometric density, symmetry type, and surface texture. The human curated 40 candidates through three rounds of review, then composed them into a 3x4 grid with deliberate chromatic sequencing -- warm to cool across each row, increasing density from top to bottom. The final prints were exhibited at 40x40 inches each.

**Process metrics**: 500 candidates generated, 40 selected in curation, 12 in final composition. Human decision points: 552 (accept/reject/annotate). Generation time: 4 hours. Curation time: 6 hours. Composition time: 8 hours. Authorship position: Curation (AI generates material pool, human selects and arranges).

### Example 2: Emergent Scores

A 20-minute musical composition created through human-AI dialogue. The AI generated 200 four-bar phrases in response to structured prompts specifying mode, tempo range, rhythmic density, and timbral characteristics. The human musician selected 35 phrases, arranged them into a five-movement structure (ABCBA), and recorded live improvisations over the AI-generated backing. The final mix interweaves AI-generated phrases with human performance, creating a texture where the listener cannot reliably distinguish which parts are human and which are machine -- and the piece's conceptual weight lies precisely in that uncertainty.

**Process metrics**: 200 phrases generated, 35 selected. Human performance: 45 minutes of improvisation, edited to 20 minutes. Authorship position: Dialogue (iterative exchange between AI generation and human performance).

### Example 3: Ghost Narratives

A collection of 7 short stories (500-1,500 words each) where the AI generated opening paragraphs, the human selected and edited them, then the AI generated continuations based on the edited openings, and the process iterated until each story reached a conclusion. The resulting narratives have a distinctive quality: they begin in unexpected places (because the AI's openings explore conceptual territory the human would not have started from) but develop with increasing human intentionality (because each subsequent iteration gives the human more material to curate and more editorial control). The collection's title, "Ghost Narratives," refers to the spectral presence of the AI's initial contributions, which remain visible in the final text like a palimpsest.

### Example 4: Synaesthetic Bridge

A real-time installation where AI translates between modalities: audience-submitted text is converted to images (via text-to-image generation), images are converted to sound (via CLAP embeddings mapped to synthesis parameters), and sound is converted back to text (via audio captioning). The cycle repeats, with each translation introducing drift and distortion. Over time, the original text becomes unrecognizable, transformed through three modality translations into something entirely new. The installation makes visible the "telephone game" of cross-modal translation and asks what is preserved and what is lost when meaning crosses between sensory domains.

### Example 5: Meta-Portrait

The most self-referential work: a portrait of the AI-conductor methodology itself. The AI generates descriptions of its own creative process, the human curates these descriptions into a narrative, and the AI illustrates the narrative. The result is a visual essay about human-AI collaboration, created through human-AI collaboration, displayed as human-AI collaboration. It is the methodology turned inside out, the process documentation elevated to artwork. This example is the reason the repository exists as art, not just as a technical framework.

---

## Theory Implemented

### Harold Cohen and AARON (1973-2016)

Harold Cohen's AARON was the longest-running human-AI art collaboration in history: Cohen spent over 40 years developing a painting program that made its own compositional decisions. Cohen's insight -- that the human artist's role shifts from making marks to designing the system that makes marks -- is the foundational principle of the AI-conductor model. Example AI Collaboration extends Cohen's framework from rule-based systems to large language and image models, where the human designs not the rules but the parameter space within which the AI explores.

### Holly Herndon and Holly+ (2021-present)

Musician Holly Herndon created Holly+, an AI model trained on her voice, and invited other artists to use it. The resulting works are neither by Herndon (she did not compose them) nor by the contributing artists alone (they are using her voice, her sonic identity). This precedent directly informs the authorship spectrum: Holly+ operates in the space between Curation and Dialogue, and Herndon's critical writing about the project provides vocabulary for discussing distributed authorship in human-AI collaboration.

### Refik Anadol and Data Sculptures (2015-present)

Refik Anadol's large-scale data visualization installations demonstrate the aesthetic potential of AI-processed data at architectural scale. His work is positioned at the Augmentation end of the authorship spectrum: Anadol is clearly the author, using AI as a rendering engine for his artistic vision. Example AI Collaboration documents this position while arguing that the Dialogue position -- where AI has more creative agency -- produces aesthetically distinct outcomes worth exploring.

### The Mechanical Turk Problem

The framework directly addresses the criticism that human-AI collaboration is merely "the human doing the real work and taking credit for the AI's output" or conversely "the AI doing the real work and the human pretending they contributed." The attribution tracker logs every human and AI contribution with timestamps, creating an auditable record of the collaborative process. The process visualizer renders this log as a temporal diagram, making the back-and-forth visible. Exhibition documentation includes these process records, allowing audiences to see exactly how each work was made. Transparency about the process is not a concession to critics -- it is part of the artwork.

### Computational Creativity Theory

Margaret Boden's distinction between exploratory, combinational, and transformational creativity provides a framework for understanding what current AI systems can and cannot do. AI excels at exploratory creativity (finding novel points in a well-defined space) and combinational creativity (finding unexpected connections between known elements). It is not yet capable of transformational creativity (changing the rules of the space itself). The AI-conductor model leverages AI's strengths while relying on human judgment for the transformational decisions: redefining the prompt space, recognizing when a "mistake" is more interesting than the intended output, deciding that the project should go in a direction the AI has not been asked about.

---

## Portfolio & Exhibition

### For Grant Reviewers

This repository demonstrates:

- **Methodological innovation**: The AI-conductor model as a rigorous, documented artistic practice with clear attribution and process transparency
- **Critical engagement**: Theoretical positioning within the history of computational art (Cohen, Herndon, Anadol) and computational creativity theory (Boden)
- **Technical capability**: Multi-modal AI pipelines (visual, audio, text) with curation and composition tools
- **Exhibition readiness**: Artist statements, wall text templates, process documentation displays, and audience engagement components
- **Timeliness**: Addresses the most urgent questions in contemporary art practice (2026): authorship, agency, and aesthetics in human-AI collaboration

### For Curators

The `exhibition/` directory contains ready-to-adapt materials for showing works produced with this framework: artist statement templates that explain the AI-conductor methodology in accessible language, wall text that contextualizes the work within computational art history, and process documentation displays (screen-based or printed) that show visitors how each work was made. The methodology is itself exhibitable: the attribution tracker's temporal diagrams are visually compelling and conceptually rich, functioning as artworks in their own right.

### For Hiring Managers

This repository demonstrates expertise in: AI/ML pipeline architecture, multi-modal content generation, human-computer interaction design, technical writing for diverse audiences, and the ability to operate at the intersection of technology and humanities -- a rare and increasingly valuable combination.

---

## Related Work

- **Harold Cohen, AARON (1973-2016)**: The foundational human-AI art collaboration. AARON made autonomous compositional decisions within Cohen's rule system. Example AI Collaboration extends this paradigm to statistical models and adds explicit authorship attribution.
- **Holly Herndon, Holly+ (2021-present)**: Voice-model-based distributed authorship. Provides vocabulary and precedent for collaborative attribution in AI art.
- **Refik Anadol, "Machine Hallucinations" (2019-present)**: Large-scale AI data visualization. Demonstrates the aesthetic potential of AI at architectural scale, positioned at the Augmentation end of the authorship spectrum.
- **Sougwen Chung, "Drawing Operations" (2015-present)**: Human-robot collaborative drawing. Chung's work is the closest precedent for the Dialogue position on the authorship spectrum, with the physical robot arm as a visible co-creator.
- **Memo Akten, "Learning to See" (2017)**: Real-time neural network visualization that reveals how AI "sees" the world. Provides a model for making AI processes visible and comprehensible to audiences.
- **Anna Ridler, "Mosaic Virus" (2019)**: Dataset-as-artwork. Ridler hand-photographed thousands of tulips to create a training dataset, making the data labor visible. Informs the framework's emphasis on process transparency.

### Cross-References Within the Eight-Organ System

| Repository | Organ | Relationship |
|-----------|-------|-------------|
| [metasystem-master](https://github.com/organvm-ii-poiesis/metasystem-master) | II | Performance SDK for real-time AI-collaborative installations |
| [learning-resources](https://github.com/organvm-ii-poiesis/learning-resources) | II | AI collaboration taught in Tier 2 curriculum |
| [example-interactive-installation](https://github.com/organvm-ii-poiesis/example-interactive-installation) | II | Autonomous drift mode uses AI-collaborative generation |
| [recursive-engine](https://github.com/organvm-i-theoria/recursive-engine) | I | Theoretical foundations for recursive creative processes |
| [public-process](https://github.com/organvm-v-logos/public-process) | V | Essays on AI collaboration as building-in-public practice |

---

## Contributing

### How to Contribute

```bash
# Fork and clone
git clone https://github.com/<your-fork>/example-ai-collaboration.git
cd example-ai-collaboration
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create a feature branch
git checkout -b feature/your-contribution

# Make changes, run tests
python -m pytest tests/ -v

# Commit (conventional commits)
git commit -m "feat(pipelines): add video generation pipeline"

# Push and open a PR
git push origin feature/your-contribution
```

### Contributions Especially Welcome

- **New modality pipelines**: Video generation/curation, 3D model generation, code-as-art generation
- **Worked examples**: Document your own human-AI collaborative process using the framework. Include the process log, the curatorial decisions, and the finished work.
- **Theoretical writing**: Critical essays on authorship, agency, aesthetics, or ethics in human-AI collaboration. These will be reviewed and potentially included in the `docs/` directory.
- **Exhibition reports**: If you exhibit work made with this framework, document the audience response, the curatorial decisions, and any institutional negotiations about how to credit AI-collaborative work.
- **Pipeline improvements**: Better curation algorithms, more expressive composition tools, improved cross-modal bridges.

### Ethical Guidelines

- All AI-generated material must be attributed. The attribution tracker is not optional.
- Training data provenance must be documented. If you use a fine-tuned model, document what it was trained on.
- Exhibition materials must explain the AI-conductor methodology in accessible language. Audiences have a right to understand what they are looking at.
- The framework does not generate deepfakes, non-consensual likenesses, or material designed to deceive. The goal is transparent collaboration, not concealment of AI involvement.

---

## License & Author

**License:** [MIT](LICENSE)

**Author:** Anthony Padavano ([@4444J99](https://github.com/4444J99))

**Organization:** [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) (ORGAN-II: Poiesis)

**System:** [meta-organvm](https://github.com/meta-organvm) -- the eight-organ creative-institutional system coordinating ~80 repositories across theory, art, commerce, orchestration, public process, community, and marketing.

---

<sub>This README is a Gap-Fill Sprint portfolio document for the organvm system. It is written for grant reviewers, curators, and collaborators who want to understand the AI-conductor model as artistic methodology, how this framework implements it, and how it fits within a larger creative-institutional architecture.</sub>