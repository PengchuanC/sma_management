let current = 0;

$(document).ready(function () {

    let questionLength = $('.carousel-inner').children().length

    // 保存用户名
    $('#authSub').click(function(){
        username = $('#name').val()
        localStorage.setItem('questionnaireName', username)
    })

    // 选择选项
    $(".q-choice").click(function () {
        $(this).parent().children().removeClass('q-choice-active').addClass('q-choice');
        $(this).parent().find('i').each(function () {
            $(this).removeClass('icon-CheckboxChecked').addClass('icon-CheckboxUnchecked');
        });
        $(this).find('i').removeClass('icon-CheckboxUnchecked').addClass('icon-CheckboxChecked')
        $(this).removeClass('q-choice').addClass('q-choice-active');
    })

    // 上一题
    $('#prev').click(function () {
        current--;
        if (current === 0) {
            $('#prev').css('display', 'none')
        }

        $('.carousel').carousel('prev')

        // 问题全部展示完成
        if (current + 1 !== questionLength) {
            $('#next').css('display', 'block').siblings().css('display', 'none')
        }
    })

    // 下一题
    $('#next').click(function () {
        if (!check()) {
            $('#liveToast').toast('show')
            return
        }
        if (current === 0) {
            $('#prev').css('display', 'block')
        }
        current++;
        $('.carousel').carousel('next')

        // 问题全部展示完成
        if (current + 1 === questionLength) {
            $('#next').css('display', 'none').siblings().css('display', 'block')
        }
    })

    // 提交结果
    $('#submit').click(function () {
        if (!check()) {
            $('#liveToast').toast('show')
            return
        }
        let span = $(this).find('span');
        span.css('display', 'inline-flex');
        let result = getResults();
        let username = localStorage.getItem('questionnaireName')
        $.ajax({
            url: '/question/submit/',
            method: 'POST',
            data: {result: result, name: username},
            dataType: "json",
            traditional: true,
            success: function (r) {
                if (r.code === 0) {
                    window.location.href = '/question/success/'
                } else if (r.code === -1){
                    $('#resultToast').toast('show');
                    span.css('display', 'none');
                }
            }
        })
    })
});


// 检查当前题目是否已完成
function check() {
    let selected = $('.carousel-item.active').find('.q-choice-active')
    return selected.length === 1;

}

function getResults() {
    let result = []
    $('.carousel-item').each(function (){
        let active = $(this).find('.q-choice-active');
        let index = active.index() + 1;
        result.push(index);
    })
    return result;
}
