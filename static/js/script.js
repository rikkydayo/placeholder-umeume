document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('.clear-btn').addEventListener('click', clearForm);
    document.querySelector('.copy-btn').addEventListener('click', copyToClipboard);
});

function copyToClipboard() {
    const resultText = document.querySelector('.result-text');
    if (!resultText) {
        alert('コピーするテキストが見つかりません。');
        return;
    }
    const text = resultText.innerText;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () {
            alert('結果をクリップボードにコピーしました！');
        }, function (err) {
            alert('コピーに失敗しました: ' + err);
        });
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            alert('結果をクリップボードにコピーしました！');
        } catch (err) {
            alert('コピーに失敗しました: ' + err);
        }
        document.body.removeChild(textarea);
    }
}

function clearForm() {
    const form = document.getElementById('inputForm');
    if (form) {
        form.reset();
        form.querySelectorAll('textarea').forEach(input => input.value = '');
    }
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
        resultContainer.style.display = 'none';
    }
}