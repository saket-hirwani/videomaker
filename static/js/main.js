document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('videoForm');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const submitButton = document.getElementById('submitButton');
    
    let progressInterval;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset and show progress elements
        progressBar.style.width = '0%';
        progressBar.classList.remove('d-none');
        progressText.classList.remove('d-none');
        submitButton.disabled = true;
        
        const formData = new FormData(form);
        
        try {
            // Start progress polling
            progressInterval = setInterval(checkProgress, 1000);
            
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to generate video');
            }
            
            // Handle successful video generation
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'video.mp4';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            showAlert('Success! Your video has been generated.', 'success');
            
        } catch (error) {
            showAlert(error.message, 'danger');
        } finally {
            clearInterval(progressInterval);
            submitButton.disabled = false;
        }
    });
    
    async function checkProgress() {
        try {
            const response = await fetch('/progress');
            const data = await response.json();
            
            progressBar.style.width = `${data.progress}%`;
            progressBar.setAttribute('aria-valuenow', data.progress);
            progressText.textContent = `${data.status || 'Processing...'} (${Math.round(data.progress)}%)`;
            
            if (data.progress >= 100) {
                clearInterval(progressInterval);
            }
        } catch (error) {
            console.error('Error checking progress:', error);
        }
    }
    
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});
