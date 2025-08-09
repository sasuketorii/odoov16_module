/** @odoo-module **/

// オートコンプリートの横幅問題を修正
(function() {
    'use strict';
    
    // オートコンプリートの幅を修正する関数
    function fixAutocompleteWidth(element) {
        if (!element) return;
        
        // スタイルを直接設定
        element.style.setProperty('min-width', '400px', 'important');
        element.style.setProperty('max-width', '600px', 'important');
        element.style.setProperty('width', 'auto', 'important');
        element.style.setProperty('overflow-x', 'hidden', 'important');
        element.style.setProperty('overflow-y', 'auto', 'important');
        element.style.setProperty('max-height', '400px', 'important');
    }
    
    // MutationObserverで動的に追加される要素を監視
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.classList && node.classList.contains('ui-autocomplete')) {
                        fixAutocompleteWidth(node);
                    }
                }
            });
        });
    });
    
    // DOMが準備できたら監視開始
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }
})();