odoo.define('sasuke_backend_theme2.SidebarMenu', function (require) {
    "use strict";

    // サイドバーを常時開く初期化関数
    function initializeSidebarOpen() {
        // サイドバーを表示
        $("#sidebar_panel").css({'display':'block'});
        $(".o_action_manager").css({'margin-left': '200px','transition':'all .1s linear'});
        $(".top_heading").css({'margin-left': '200px','transition':'all .1s linear', 'width':'auto'});
        
        // ボタンの表示切り替え（閉じるボタンを非表示に）
        $("#openSidebar").hide();
        $("#closeSidebar").hide(); // 閉じるボタンも非表示
        
        // クラスの追加
        var navbar = $(".o_main_navbar");
        var navbar_id = navbar.data("id");
        $("nav").addClass(navbar_id);
        navbar.addClass("small_nav");
        
        var action_manager = $(".o_action_manager");
        var action_manager_id = action_manager.data("id");
        $("div").addClass(action_manager_id);
        action_manager.addClass("sidebar_margin");
        
        var top_head = $(".top_heading");
        var top_head_id = top_head.data("id");
        $("div").addClass(top_head_id);
        top_head.addClass("sidebar_margin");
    }

    // ページ読み込み時に初期化
    $(document).ready(function() {
        setTimeout(function() {
            initializeSidebarOpen();
        }, 100);
    });

    // DOM変更監視（OdooのSPAナビゲーション対応）
    var observer = new MutationObserver(function(mutations) {
        // サイドバーが存在し、表示されていない場合は再初期化
        if ($('#sidebar_panel').length && $('#sidebar_panel').css('display') === 'none') {
            initializeSidebarOpen();
        }
    });

    // 監視開始
    $(document).ready(function() {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });

    // メニュー項目クリック時もサイドバーを開いたままにする
    $(document).on("click", ".sidebar a", function(event){
        var menu = $(".sidebar a");
        var $this = $(this);
        var id = $this.data("id");
        $("header").removeClass().addClass(id);
        menu.removeClass("active");
        $this.addClass("active");
        
        // サイドバーは閉じない（常時表示のため）
        // 以下の処理をコメントアウト
        /*
        $("#sidebar_panel").css({'display':'none'});
        $(".o_action_manager").css({'margin-left': '0px'});
        $(".top_heading").css({'margin-left': '0px', 'width':'100%'});
        */
        
        // マージンは維持
        setTimeout(function() {
            initializeSidebarOpen();
        }, 50);
    });
    
    // サイドバートグルボタンを無効化（常時表示のため）
    $(document).on("click", "#closeSidebar", function(event){
        event.preventDefault();
        // 何もしない（常時表示のため）
    });
    
    $(document).on("click", "#openSidebar", function(event){
        event.preventDefault();
        // 何もしない（常時表示のため）
    });
});