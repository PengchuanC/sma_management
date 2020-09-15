
$(function () {
    // 切换菜单tab
    $('.item').click(function () {
        $(this).addClass('active').siblings().removeClass("active");
    });

    // 问卷单选
    $('.q-choice').click(function () {
        let input = $(this).find('input');
        if (input.is(':checked')){
            input.removeAttr('checked')
        } else {
            input.attr('checked', true)
        }
        $(this).siblings().each(function(_, x){$(x).find('input').removeAttr('checked')});
        $(this).parents('div.q-quest-area').children('h5').removeClass('q-undo');
    });

    // 检查题目
    $('#check').click(function () {
        $('.q-quest-area').each(function (_, x){
            let checked = false;
            $(x).find('.q-choice').each(function (_, y){
                if ($(y).find('input').is(':checked')){
                    checked = true;
                    return false;
                }
            })
            if (!checked){
                $(x).children("h5").addClass('q-undo')
            } else {
                $(x).children("h5").removeClass('q-undo')
            }
        })
    });
})