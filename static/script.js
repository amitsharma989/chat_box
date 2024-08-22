document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const pdfFileInput = document.getElementById('pdfFile');
    const pdfTextArea = document.getElementById('pdfText');
    const queryInput = document.getElementById('queryInput');
    const askButton = document.getElementById('askButton');
    const responseArea = document.getElementById('responseArea');

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const file = pdfFileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload_pdf/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                pdfTextArea.value = result.text || 'No text extracted from PDF.';
            } else {
                pdfTextArea.value = 'Error uploading PDF.';
            }
        } catch (error) {
            pdfTextArea.value = 'Error: ' + error.message;
        }
    });

    askButton.addEventListener('click', async () => {
        const question = queryInput.value; 
    
        if (!question) {
            responseArea.innerText = 'Please enter a question.';
            return;
        }
    
        try {
            const response = await fetch('/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });
    
            if (response.ok) {
                const result = await response.json();
                responseArea.innerText = result.answer || 'No answer found.';
            } else {
                responseArea.innerText = 'Error asking question.';
            }
        } catch (error) {
            responseArea.innerText = 'Error: ' + error.message;
        }
    });
    
});
