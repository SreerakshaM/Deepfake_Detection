document.addEventListener('DOMContentLoaded', () => {
    const imageInput = document.getElementById('image-input');
    const results = document.getElementById('results');
    const predictionText = document.getElementById('prediction-text');
    const labelText = document.getElementById('label-text');
    const probFill = document.getElementById('prob-fill');

    // NEW Elements
    const previewSection = document.getElementById('preview-section');
    const previewImg = document.getElementById('user-preview-img');
    const previewFrame = document.querySelector('.preview-frame');
    const dataStream = document.getElementById('data-stream');

    // Simulate HUD Data stream
    setInterval(() => {
        if (previewSection.style.display === 'block') {
            let stream = '';
            for (let i = 0; i < 5; i++) {
                stream += '0x' + Math.floor(Math.random() * 16777215).toString(16).toUpperCase().padStart(6, '0') + '<br>';
            }
            dataStream.innerHTML = stream;
        }
    }, 150);

    const videoInput = document.getElementById('video-input');

    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleUpload(file);
    });

    videoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleUpload(file);
    });

    async function handleUpload(file) {
        // Handle UI Preview
        const isVideo = file.type.startsWith('video/');
        let vid = document.getElementById('user-preview-vid');

        if (isVideo) {
            if (!vid) {
                vid = document.createElement('video');
                vid.id = 'user-preview-vid';
                vid.autoplay = true; vid.loop = true; vid.muted = true;
                Object.assign(vid.style, {
                    width: '100%', height: '100%', objectFit: 'cover',
                    borderRadius: '12px', zIndex: '1', position: 'relative'
                });
                previewFrame.insertBefore(vid, previewFrame.firstChild);
            }
            previewImg.style.display = 'none';
            vid.style.display = 'block';
            vid.src = URL.createObjectURL(file);
            previewSection.style.display = 'block';
            previewFrame.classList.add('scanning');
        } else {
            if (vid) vid.style.display = 'none';
            previewImg.style.display = 'block';

            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                previewSection.style.display = 'block';
                previewFrame.classList.add('scanning');
            };
            reader.readAsDataURL(file);
        }

        // Show results waiting state
        results.style.display = 'block';

        predictionText.innerText = 'WAIT...';
        labelText.innerText = 'ANALYZING';
        probFill.style.width = '0%';
        probFill.style.background = 'var(--text-muted)';
        probFill.style.boxShadow = 'none';
        document.querySelector('.result-panel').style.borderLeftColor = 'var(--accent-cyan)';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            previewFrame.classList.remove('scanning'); // Stop scan on result

            if (data.error) {
                alert(data.error);
                return;
            }

            // Update UI with results
            const prob = data.prediction * 100;
            
            // If authentic, show the confidence of it being authentic (100 - prob)
            // If fake, show the confidence of it being fake (prob)
            const displayProb = data.label === 'AI_GENERATED' ? prob : (100 - prob);
            
            predictionText.innerText = `${displayProb.toFixed(1)}%`;
            probFill.style.width = `${displayProb}%`;

            // Styling based on result
            document.getElementById('analysis-details').style.display = 'block';
            document.getElementById('basis-text').innerText = data.basis || "Numerical analysis of frequency spectrum.";
            document.getElementById('comparison-text').innerText = data.comparison || "Baseline comparison complete.";
            document.getElementById('hf-noise-val').innerText = data.metrics?.high_frequency_noise ? data.metrics.high_frequency_noise + '%' : '--';
            document.getElementById('spectral-energy-val').innerText = data.metrics?.spectral_energy || '--';

            if (data.label === 'AI_GENERATED') {
                labelText.innerText = "YY IT IS AI IMAGE";
                predictionText.style.color = 'var(--accent-red)';
                probFill.style.background = 'var(--accent-red)';
                probFill.style.boxShadow = '0 0 10px var(--accent-red)';
                document.querySelector('.result-panel').style.borderLeftColor = 'var(--accent-red)';
                previewFrame.style.borderColor = 'var(--accent-red)';
                previewFrame.style.boxShadow = '0 0 20px rgba(255, 62, 108, 0.2)';
            } else {
                labelText.innerText = "YY IT IS REAL";
                predictionText.style.color = 'var(--accent-cyan)';
                probFill.style.background = 'var(--accent-cyan)';
                probFill.style.boxShadow = '0 0 10px var(--accent-cyan)';
                document.querySelector('.result-panel').style.borderLeftColor = 'var(--accent-cyan)';
                previewFrame.style.borderColor = 'var(--accent-cyan)';
                previewFrame.style.boxShadow = '0 0 20px rgba(0, 242, 255, 0.1)';
            }

        } catch (error) {
            console.error('Error:', error);
            previewFrame.classList.remove('scanning');
            predictionText.innerText = 'ERR';
            labelText.innerText = 'CONNECTION LOST';
            predictionText.style.color = 'var(--accent-red)';
        }
    }
});
