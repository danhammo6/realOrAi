// Image dataset for Real or AI?
// Add or remove entries below — the game picks a balanced set per round.
// All images sourced from Wikimedia Commons under free licenses (public domain / CC).

const IMAGES = [
  // ========== AI-generated ==========
  { src: "images/ai/hedgehog.jpg",           isAI: true,  alt: "Hedgehog",          caption: "AI-generated hedgehog" },
  { src: "images/ai/arctic_wolf.png",        isAI: true,  alt: "Arctic wolf",       caption: "AI-generated — Recraft v3" },
  { src: "images/ai/wolf_moon.jpg",          isAI: true,  alt: "Wolf",              caption: "AI-generated wolf scene" },
  { src: "images/ai/dragon_sunset.png",      isAI: true,  alt: "Dragon at sunset",  caption: "AI-generated — FLUX 1.1 Pro Ultra" },
  { src: "images/ai/moonlit_forest.jpg",     isAI: true,  alt: "Moonlit forest",    caption: "AI-generated — ChatGPT" },
  { src: "images/ai/cold_mountains.jpg",     isAI: true,  alt: "Mountains",         caption: "AI-generated landscape" },
  { src: "images/ai/firefly_landscape.jpg",  isAI: true,  alt: "Landscape",         caption: "AI-generated — Adobe Firefly" },
  { src: "images/ai/fusion_island.png",      isAI: true,  alt: "Island",            caption: "AI-generated island — ChatGPT" },
  { src: "images/ai/ai_food_dish.jpg",       isAI: true,  alt: "Food dish",         caption: "AI-generated food dish" },
  { src: "images/ai/green_apple.png",        isAI: true,  alt: "Green apple",       caption: "AI-generated apple" },
  { src: "images/ai/nun_butterfly.png",      isAI: true,  alt: "Nun and butterfly", caption: "AI-generated — Microsoft Copilot" },
  { src: "images/ai/elderly_lady.png",       isAI: true,  alt: "Elderly lady",      caption: "AI-generated portrait — Copilot" },
  { src: "images/ai/controlnet_portrait.png",isAI: true,  alt: "Portrait",          caption: "AI-generated — ControlNet / Stable Diffusion" },
  { src: "images/ai/frulli_frulla.jpg",      isAI: true,  alt: "Creature",          caption: "AI-generated creature" },
  { src: "images/ai/dalle_writer.webp",      isAI: true,  alt: "Writer illustration", caption: "AI-generated — DALL-E" },
  { src: "images/ai/grok_library.jpg",       isAI: true,  alt: "Library",           caption: "AI-generated library — Grok" },
  { src: "images/ai/street_scene.jpg",       isAI: true,  alt: "Street scene",      caption: "AI-generated street scene — Blockade Labs" },

  // ========== Real photos ==========
  { src: "images/real/leopard.jpg",          isAI: false, alt: "Leopard",           caption: "Real photo — Featured Picture on Commons" },
  { src: "images/real/rainbow.jpg",          isAI: false, alt: "Rainbow",           caption: "Real photo — Yorkshire, UK" },
  { src: "images/real/viaduct.jpg",          isAI: false, alt: "Viaduct",           caption: "Real photo — Ribblehead Viaduct, UK" },
  { src: "images/real/big_mac.jpg",          isAI: false, alt: "Hamburger",         caption: "Real photo — Big Mac hamburger" },
  { src: "images/real/apple_cake.jpg",       isAI: false, alt: "Apple cake",        caption: "Real photo — apple cake with ice cream" },
  { src: "images/real/bleu_de_gex.jpg",      isAI: false, alt: "Cheese",            caption: "Real photo — Bleu de Gex cheese" },
  { src: "images/real/beetroots.jpg",        isAI: false, alt: "Beetroots",         caption: "Real photo — beetroots in a basket" },
  { src: "images/real/asparagus_soup.jpg",   isAI: false, alt: "Asparagus soup",    caption: "Real photo — asparagus soup" },
  { src: "images/real/flower_butterfly.jpg", isAI: false, alt: "Flower",            caption: "Real photo — flower with butterfly" },
  { src: "images/real/swaledale.jpg",        isAI: false, alt: "Swaledale",         caption: "Real photo — Swaledale, UK" },
  { src: "images/real/yorkshire_road.jpg",   isAI: false, alt: "Country road",      caption: "Real photo — Yorkshire Dales" },
  { src: "images/real/grilled_trout.jpg",    isAI: false, alt: "Grilled trout",     caption: "Real photo — grilled trout" },
  { src: "images/real/coral.jpg",            isAI: false, alt: "Coral",             caption: "Real photo — ascidian on soft coral" },
  { src: "images/real/shrimp_shells.jpg",    isAI: false, alt: "Shrimp shells",     caption: "Real photo — shrimp shells on plate" },

  // ========== Real artworks (not AI!) ==========
  { src: "images/real/starry_night.jpg",     isAI: false, alt: "The Starry Night",           caption: "Real — Van Gogh, 'The Starry Night' (1889)" },
  { src: "images/real/mona_lisa.jpg",        isAI: false, alt: "Mona Lisa",                  caption: "Real — Leonardo da Vinci, 'Mona Lisa' (c. 1503)" },
  { src: "images/real/great_wave.jpg",       isAI: false, alt: "Great Wave off Kanagawa",    caption: "Real — Hokusai, 'The Great Wave off Kanagawa' (c. 1831)" },
  { src: "images/real/sunflowers.jpg",       isAI: false, alt: "Sunflowers",                 caption: "Real — Van Gogh, 'Sunflowers' (1888)" },
  { src: "images/real/klimt_kiss.jpg",       isAI: false, alt: "The Kiss",                   caption: "Real — Gustav Klimt, 'The Kiss' (1907–08)" },
  { src: "images/real/american_gothic.jpg",  isAI: false, alt: "American Gothic",            caption: "Real — Grant Wood, 'American Gothic' (1930)" },
  { src: "images/real/pearl_earring.jpg",    isAI: false, alt: "Girl with a Pearl Earring",  caption: "Real — Vermeer, 'Girl with a Pearl Earring' (c. 1665)" },
  { src: "images/real/bosch_garden.jpg",     isAI: false, alt: "Garden of Earthly Delights", caption: "Real — Hieronymus Bosch, 'The Garden of Earthly Delights'" },
  { src: "images/real/monet_sunrise.jpg",    isAI: false, alt: "Impression, Sunrise",        caption: "Real — Monet, 'Impression, Sunrise' (1872)" },
  { src: "images/real/birth_of_venus.jpg",   isAI: false, alt: "The Birth of Venus",         caption: "Real — Botticelli, 'The Birth of Venus' (c. 1485)" },
  { src: "images/real/tower_babel.jpg",      isAI: false, alt: "Tower of Babel",             caption: "Real — Bruegel, 'The Tower of Babel' (1563)" },
];
