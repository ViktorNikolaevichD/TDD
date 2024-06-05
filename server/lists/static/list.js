window.Superlists = {};
window.Superlists.initialize = function () {
    $('input[name="text"]').on('click keypress', function () {
        $('.has-error').hide();
    });
};
