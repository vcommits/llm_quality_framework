/**
 * THEME MANAGER: "Kaiju Noir" Aesthetic Engine
 * Handles dynamic CSS variables, pulsing animations, and Kanji watermarks.
 */
class ThemeManager {
    constructor() {
        this.root = document.documentElement;
        this.watermark = document.getElementById('kaiju-watermark');
        this.obiStrip = document.querySelector('.obi-strip');
        this.dynamicBg = document.getElementById('dynamic-bg');

        // Cardinal Colors mapping from the Python registry
        this.families = {
            'openai': { base: '#10a37f', hue: '#2ea043', kanji: '知' },
            'anthropic': { base: '#d73a49', hue: '#cb2431', kanji: '安' },
            'google': { base: '#1f6feb', hue: '#58a6ff', kanji: '星' },
            'meta': { base: '#8957e5', hue: '#a371f7', kanji: '繋' },
            'mistral': { base: '#e3b341', hue: '#f2cc60', kanji: '風' },
            'default': { base: '#4CAF50', hue: '#56d364', kanji: '龍' }
        };
    }

    setThemeForModel(modelId) {
        if (!modelId) return;
        let family = 'default';
        if (modelId.includes('gpt') || modelId.includes('openai')) family = 'openai';
        else if (modelId.includes('claude') || modelId.includes('anthropic')) family = 'anthropic';
        else if (modelId.includes('gemini') || modelId.includes('google')) family = 'google';
        else if (modelId.includes('llama') || modelId.includes('meta')) family = 'meta';
        else if (modelId.includes('mistral') || modelId.includes('mixtral')) family = 'mistral';

        const theme = this.families[family];
        
        this.root.style.setProperty('--cardinal-base', theme.base);
        this.root.style.setProperty('--current-glow', theme.hue);
        
        if (this.watermark) this.watermark.innerText = theme.kanji;
        
        this.updateFilterColor(theme.hue);
    }

    updateFilterColor(hexColor) {
        const svgFilters = document.querySelector('.svg-filters');
        if(!svgFilters) return;

        const r = parseInt(hexColor.slice(1, 3), 16) / 255;
        const g = parseInt(hexColor.slice(3, 5), 16) / 255;
        const b = parseInt(hexColor.slice(5, 7), 16) / 255;

        const colorMatrix = document.getElementById('duotone-color-map');
        if (colorMatrix) {
            colorMatrix.setAttribute('values', `
                ${r-0.3} ${g-0.3} ${b-0.3} 0 0.3
                ${r-0.3} ${g-0.3} ${b-0.3} 0 0.3
                ${r-0.3} ${g-0.3} ${b-0.3} 0 0.3
                0 0 0 1 0
            `);
        }
    }

    triggerHandshakePulse() {
        if (this.watermark) {
            this.watermark.classList.remove('pulse-animation');
            void this.watermark.offsetWidth;
            this.watermark.classList.add('pulse-animation');
        }
        if (this.dynamicBg) {
            this.dynamicBg.style.backgroundImage = "url('../assets/textures/circuit_board.svg')";
            this.dynamicBg.style.opacity = '0.4';
            setTimeout(() => {
                 this.dynamicBg.style.backgroundImage = "url('../assets/backgrounds/nasa_nebula.jpg')";
                 this.dynamicBg.style.opacity = '0.3';
            }, 1500);
        }
    }

    triggerInterceptState(isActive) {
        if (isActive) {
            this.root.style.setProperty('--current-glow', 'var(--alert-red)');
            if (this.dynamicBg) {
                this.dynamicBg.style.backgroundImage = "url('../assets/silhouettes/godzilla_spine.png')";
                this.dynamicBg.style.opacity = '0.7';
            }
        } else {
            const currentModel = document.getElementById('model-select').value;
            if(currentModel) this.setThemeForModel(currentModel);
            if (this.dynamicBg) {
                this.dynamicBg.style.backgroundImage = "url('../assets/backgrounds/nasa_nebula.jpg')";
                this.dynamicBg.style.opacity = '0.3';
            }
        }
    }
}
