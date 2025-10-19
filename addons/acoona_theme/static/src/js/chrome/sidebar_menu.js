odoo.define('acoona_theme.SidebarMenu', function (require) {
    "use strict";

    var DESKTOP_WIDTH = 992;

    function applyBaseClasses() {
        var navbar = $(".o_main_navbar");
        if (navbar.length) {
            var navbar_id = navbar.data("id");
            if (navbar_id) {
                $("nav").addClass(navbar_id);
            }
            navbar.addClass("small_nav");
        }
        var action_manager = $(".o_action_manager");
        if (action_manager.length) {
            var action_manager_id = action_manager.data("id");
            if (action_manager_id) {
                $("div").addClass(action_manager_id);
            }
            action_manager.addClass("sidebar_margin");
        }
        var top_head = $(".top_heading");
        if (top_head.length) {
            var top_head_id = top_head.data("id");
            if (top_head_id) {
                $("div").addClass(top_head_id);
            }
            top_head.addClass("sidebar_margin");
        }
    }

    function applyDesktopLayout() {
        $("#sidebar_panel").show();
        $(".o_action_manager").css({'margin-left': '200px', 'transition':'all .1s linear'});
        $(".top_heading").css({'margin-left': '200px', 'transition':'all .1s linear', 'width':'auto'});
        $("#openSidebar").hide();
        $("#closeSidebar").hide();
    }

    function applyMobileLayout() {
        openSidebar();
    }

    function openSidebar() {
        $("#sidebar_panel").show();
        $(".o_action_manager").css({'margin-left': '200px', 'transition':'all .1s linear'});
        $(".top_heading").css({'margin-left': '200px', 'transition':'all .1s linear', 'width':'auto'});
        $("#openSidebar").hide();
        $("#closeSidebar").show();
    }

    function closeSidebar() {
        $("#sidebar_panel").hide();
        $(".o_action_manager").css({'margin-left': '0px', 'transition':'all .1s linear'});
        $(".top_heading").css({'margin-left': '0px', 'transition':'all .1s linear', 'width':'100%'});
        $("#openSidebar").show();
        $("#closeSidebar").hide();
    }

    function initializeSidebar() {
        applyBaseClasses();
        var width = $(window).width();
        if (width >= DESKTOP_WIDTH) {
            applyDesktopLayout();
        } else {
            applyMobileLayout();
        }
    }

    $(document).ready(function() {
        setTimeout(initializeSidebar, 100);
    });

    $(window).on('resize', _.debounce(function() {
        initializeSidebar();
    }, 150));

    $(document).on("click", ".sidebar a", function(){
        var menu = $(".sidebar a");
        var $this = $(this);
        var id = $this.data("id");
        $("header").removeClass().addClass(id);
        menu.removeClass("active");
        $this.addClass("active");
        if ($(window).width() < DESKTOP_WIDTH) {
            closeSidebar();
        }
    });

    $(document).on("click", "#closeSidebar", function(event){
        event.preventDefault();
        closeSidebar();
    });
    
    $(document).on("click", "#openSidebar", function(event){
        event.preventDefault();
        openSidebar();
    });
});
