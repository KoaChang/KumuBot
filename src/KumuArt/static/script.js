document.addEventListener('DOMContentLoaded', function() {
    var submitButton = document.getElementById('artsubmit-btn');
    var descriptionInput = document.getElementById('artdescription');
    var imageElement = document.getElementById('artimage');
    var outputContainer = document.getElementById('artoutput');
    var factContainer = document.getElementById('artfact');
    var imagePlaceholder = document.getElementById('image-placeholder');
    var factPlaceholder = document.getElementById('fact-placeholder');

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function renderMarkdown(markdown) {
        var normalized = escapeHtml(markdown || '').replace(/\r\n?/g, '\n').trim();
        if (!normalized) {
            return '';
        }

        function formatInline(text) {
            var codeSpans = [];
            var formatted = text.replace(/`([^`]+)`/g, function(_, code) {
                codeSpans.push(code);
                return '@@CODE' + (codeSpans.length - 1) + '@@';
            });

            formatted = formatted.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
            formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            formatted = formatted.replace(/__([^_]+)__/g, '<strong>$1</strong>');
            formatted = formatted.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
            formatted = formatted.replace(/(^|[^_])_([^_\n]+)_(?!_)/g, '$1<em>$2</em>');

            return formatted.replace(/@@CODE(\d+)@@/g, function(_, index) {
                return '<code>' + codeSpans[Number(index)] + '</code>';
            });
        }

        var lines = normalized.split('\n');
        var html = [];
        var paragraphLines = [];
        var listItems = [];
        var listType = null;

        function flushParagraph() {
            if (!paragraphLines.length) {
                return;
            }
            html.push('<p>' + formatInline(paragraphLines.join('<br>')) + '</p>');
            paragraphLines = [];
        }

        function flushList() {
            if (!listItems.length || !listType) {
                return;
            }
            html.push('<' + listType + '>' + listItems.map(function(item) {
                return '<li>' + formatInline(item) + '</li>';
            }).join('') + '</' + listType + '>');
            listItems = [];
            listType = null;
        }

        lines.forEach(function(line) {
            var trimmed = line.trim();

            if (!trimmed) {
                flushParagraph();
                flushList();
                return;
            }

            var headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
            if (headingMatch) {
                flushParagraph();
                flushList();
                var level = headingMatch[1].length;
                html.push('<h' + level + '>' + formatInline(headingMatch[2]) + '</h' + level + '>');
                return;
            }

            var unorderedMatch = trimmed.match(/^[-*]\s+(.*)$/);
            if (unorderedMatch) {
                flushParagraph();
                if (listType && listType !== 'ul') {
                    flushList();
                }
                listType = 'ul';
                listItems.push(unorderedMatch[1]);
                return;
            }

            var orderedMatch = trimmed.match(/^\d+\.\s+(.*)$/);
            if (orderedMatch) {
                flushParagraph();
                if (listType && listType !== 'ol') {
                    flushList();
                }
                listType = 'ol';
                listItems.push(orderedMatch[1]);
                return;
            }

            flushList();
            paragraphLines.push(trimmed);
        });

        flushParagraph();
        flushList();
        return html.join('');
    }

    function startLoadingAnimation() {
        submitButton.innerHTML = 'Loading<span class="loading-dots"></span>';
        submitButton.disabled = true;
    }

    function stopLoadingAnimation() {
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;
    }

    function submitDescription() {
        var description = descriptionInput.value.trim();

        if (!description) {
            outputContainer.textContent = 'Please enter a description!';
            return;
        }

        outputContainer.textContent = '';
        descriptionInput.disabled = true;
        startLoadingAnimation();

        factContainer.innerHTML = '';
        imageElement.style.display = 'none';
        factContainer.style.display = 'none';
        imagePlaceholder.style.display = 'block';
        factPlaceholder.style.display = 'block';

        fetch('https://kumubot.pythonanywhere.com/art', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description: description })
        })
        .then(response => response.json())
        .then(data => {
            imageElement.src = data.image_url;
            factContainer.innerHTML = renderMarkdown(data.fun_fact);

            imageElement.style.display = 'block';
            factContainer.style.display = 'block';
            imagePlaceholder.style.display = 'none';
            factPlaceholder.style.display = 'none';

            descriptionInput.disabled = false;
            stopLoadingAnimation();
        })
        .catch(error => {
            console.error('Error:', error);
            outputContainer.textContent = 'Error occurred while generating image.';
            descriptionInput.disabled = false;
            stopLoadingAnimation();
        });
    }

    submitButton.addEventListener('click', submitDescription);

    descriptionInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            submitDescription();
        }
    });
});
