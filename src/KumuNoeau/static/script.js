document.addEventListener('DOMContentLoaded', function() {
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

  document.getElementById("noeauuserInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      document.getElementById("oleloForm").dispatchEvent(new Event('submit'));
    }
  });

  document.getElementById("oleloForm").addEventListener("submit", function(event){
    event.preventDefault();

    let userInputElement = document.getElementById("noeauuserInput");
    userInputElement.disabled = true;

    let userInput = userInputElement.value;
    let generateNew = document.getElementById("generateCheckbox").checked;
    let button = document.getElementById("noeausubmitButton");
    let originalButtonText = button.innerText;

    button.innerHTML = `Loading<span class="loading-dots"></span>`;
    button.disabled = true;

    document.querySelector('.response-area').classList.remove('empty');

    fetch('https://kumubot.pythonanywhere.com/noeau', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userInput, generateNew }),
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById("noeauserverResponse").innerHTML = renderMarkdown(data.message);
      userInputElement.disabled = false;
      button.innerHTML = originalButtonText;
      button.disabled = false;
    })
    .catch((error) => {
      console.error('Error:', error);
      document.getElementById("noeauserverResponse").innerHTML = renderMarkdown("An error occurred. Please try again.");
      userInputElement.disabled = false;
      button.innerHTML = originalButtonText;
      button.disabled = false;
    });
  });

  document.getElementById("generateCheckbox").addEventListener("change", function(){
    if(this.checked) {
      document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau create its own new ʻŌlelo Noʻeau";
    } else {
      document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau find existing 'Ōlelo Noʻeau";
    }
  });

  document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau find existing 'Ōlelo Noʻeau";
});
