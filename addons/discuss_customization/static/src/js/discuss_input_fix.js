/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from '@mail/components/composer/composer';
import { onMounted } from '@odoo/owl';

// Composerコンポーネントにパッチを適用
patch(Composer.prototype, 'discuss_customization.Composer', {
    /**
     * キーダウンイベントをオーバーライド
     * Enterキーの挙動を変更
     */
    _onKeydown(ev) {
        // Cmd(Mac) または Ctrl(Windows/Linux) + Enter で送信
        if ((ev.metaKey || ev.ctrlKey) && ev.key === 'Enter') {
            ev.preventDefault();
            ev.stopPropagation();
            ev.stopImmediatePropagation();
            
            // テキストがある場合のみ送信
            const content = this.composer.textInputContent;
            if (content && content.trim()) {
                this.composer.postMessage();
            }
            return false;
        }
        
        // Shift + Enter で改行
        if (ev.shiftKey && ev.key === 'Enter') {
            // デフォルトの改行動作を許可
            return this._super(...arguments);
        }
        
        // Enter のみの場合は改行を挿入（送信しない）
        if (ev.key === 'Enter' && !ev.shiftKey && !ev.metaKey && !ev.ctrlKey) {
            ev.preventDefault();
            ev.stopPropagation();
            ev.stopImmediatePropagation();
            
            // 改行を挿入
            const textarea = ev.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const value = textarea.value;
            
            textarea.value = value.substring(0, start) + '\n' + value.substring(end);
            textarea.selectionStart = textarea.selectionEnd = start + 1;
            
            // 入力イベントをトリガー
            const inputEvent = new Event('input', { bubbles: true });
            textarea.dispatchEvent(inputEvent);
            
            return false;
        }
        
        // その他のイベントは親クラスの処理を実行
        return this._super(...arguments);
    },
    
    /**
     * コンポーネントのセットアップ時に追加の初期化
     */
    setup() {
        this._super(...arguments);
        
        // テキストエリアの初期化処理を追加
        onMounted(() => {
            const textarea = this.el?.querySelector('textarea');
            if (textarea) {
                // スタイルを適用
                textarea.style.backgroundColor = '#ffffff';
                textarea.style.color = '#000000';
                textarea.style.minHeight = '40px';
                
                // プレースホルダー設定
                if (!textarea.placeholder) {
                    textarea.placeholder = 'メッセージを入力... (Cmd/Ctrl+Enter で送信)';
                }
                
                // キーダウンイベントリスナーを追加
                textarea.addEventListener('keydown', (ev) => {
                    this._onKeydown(ev);
                }, true);
            }
        });
    }
});