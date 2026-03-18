document.addEventListener('DOMContentLoaded', function() {
    var submitButton = document.getElementById("dicsubmitButton");
    var searchInput = document.getElementById("dicsearchInput");
    var responseContainer = document.getElementById("dicresponse");
    var responseArea = document.querySelector(".response-area");

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
        submitButton.innerHTML = `Loading<span class="loading-dots"></span>`;
        submitButton.disabled = true;
    }
    
    function stopLoadingAnimation() {
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;
    }
    
    function processInput() {
        var userInput = searchInput.value;
        if (!userInput.trim()) {
            return; // Don't process empty inputs
        }
        
        searchInput.disabled = true;
        startLoadingAnimation();
        
        // Remove empty class to show response area is active
        responseArea.classList.remove('empty');
        
        fetch('https://kumubot.pythonanywhere.com/dictionary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search: userInput
            }),
        })
        .then(response => response.json())
        .then(data => {
            responseContainer.innerHTML = renderMarkdown(data.result);
            searchInput.disabled = false;
            stopLoadingAnimation();
        })
        .catch((error) => {
            console.error('Error:', error);
            responseContainer.innerHTML = renderMarkdown('An error occurred. Please try again.');
            searchInput.disabled = false;
            stopLoadingAnimation();
        });
    }
    
    submitButton.addEventListener('click', processInput);
    
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            processInput();
        }
    });
});
