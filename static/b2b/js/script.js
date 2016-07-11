var CUT_OFF = 2;
var X_MAX = 31; // for year : 12, for week : 7, for day: 24, for month: 31
var backUpData = [];
var myChart = [];
var tick_x = [];
var TIME_FILTER = 'MONTH'; // YEAR, MONTH, WEEK, DAY, || YEARLY, MONTHLY, WEEKLY, DAILY
var TYPE_FILTER = 6; // QS1:0, QS2:1, QS3:2, QS4:3, QD1:4, QD2:5, OVERALL:6 
$(function () {

    //Sidebar
    $("#menu-toggle").click(function (e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });

    //Initialize Bootstrap material
    $.material.init();

    //Echarts
    require.config({
        paths: {
            echarts: "/static/b2b/js/echarts/"
        }
    });

    //DASHBOARD---------------
    //NEWS TICKER
    var newsTicker = $('#newsTicker').newsTicker({
        row_height: 80
        , max_rows: 5
        , duration: 4000
    });

    $("#timeDaily").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'DAILY';
        X_MAX = 24;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeWeekly").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'WEEKLY';
        X_MAX = 7;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeMonthly").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'MONTHLY';
        X_MAX = 31;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeYearly").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'YEARLY';
        X_MAX = 12;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeYear").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'YEAR';
        X_MAX = 12;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeMonth").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'MONTH';
        X_MAX = 31;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeWeek").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'WEEK';
        X_MAX = 7;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    $("#timeDay").click(function () {
        TYPE_FILTER = 6;
        TIME_FILTER = 'DAY';
        X_MAX = 24;
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
        loadDashboard(backUpData);
    });

    //FEEDBACKS PAGE---------------
    $("#allFilter").click(function () {
        $(".grey").fadeIn();
        $(".green").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#greyFilter").click(function () {
        $(".grey").fadeIn();
        $(".green").fadeOut();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#greenFilter").click(function () {
        $(".green").fadeIn();
        $(".grey").fadeOut();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#commentFilter").click(function () {
        $(".nocomment").fadeOut();
        $(".comment").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#nocommentFilter").click(function () {
        $(".comment").fadeOut();
        $(".nocomment").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#starFilter").click(function () {
        $(".unstarred").fadeOut();
        $(".starred").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#unstarFilter").click(function () {
        $(".starred").fadeOut();
        $(".unstarred").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#returningFilter").click(function () {
        $(".nonreturning").fadeOut();
        $(".returning").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });
    $("#nonreturningFilter").click(function () {
        $(".returning").fadeOut();
        $(".nonreturning").fadeIn();
        $(this).parent().children().removeClass('active');
        $(this).addClass('active');
    });

    $(".toggleStar").click(function (event) {
        var status = 0;
        if (this.checked) {
            status = 1;
            var par = $(this).parent().parent().parent().parent();
            par.removeClass('unstarred');
            par.addClass('starred');
        } else {
            var par = $(this).parent().parent().parent().parent();
            par.removeClass('starred');
            par.addClass('unstarred');
        }
        $.ajax({
            type: "POST"
            , url: "/accounts/profile/feedbacks/post/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , id: $(this).attr('name')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    //STAFF PROMO SMS
    $("#promosmsTypeCheckbox").click(function (event) {
        if (this.checked) {
            $("#b_entity").fadeIn();
        } else {
            $("#b_entity").fadeOut();
        }
    });

    $(".promoTemplateActive").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/staff/dashboard/promosms/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , id: $(this).attr('name')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    // STAFF SMS ACCOUNTS
    $(".smsAccountActive").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/staff/dashboard/smsaccount/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , id: $(this).attr('name')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    $(".smsAccountTransActive").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/staff/dashboard/smsaccount/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , idt: $(this).attr('name')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    //STAFF PACKAGES
    $('select#package').change(function () {
        package = $('select#package').find(':selected').val();
        $("#" + package).fadeOut();
    });

    //STAFF BUY
    var companyBalance = 0;
    $('select#b_entity').change(function () {
        companyBalance = parseFloat($('select#b_entity').find(':selected').data('bal'));
        $('#balance').html(companyBalance);
        $('#balanceLeft').html(companyBalance);
        if (parseFloat($('select#b_entity').find(':selected').data('bal'))) {
            $("input#quantity").prop('disabled', false);
        } else {
            $("input#quantity").prop('disabled', true);
        }
    });
    $('input#quantity').change(function () {
        var amount = parseFloat($('#price').text()) * parseFloat($(this).val());
        $('#amount').html(amount);
        $('#balanceLeft').html(companyBalance - amount);
        if (amount >= companyBalance) {
            $('input#quantity').attr('max', Math.floor(companyBalance / parseFloat($('#price').text())));
            $('#quantityHelpBlock').html('Balance Limit Reached!');
        }
    });

    //EMPLOYEE PIN GENERATION
    $("#generatePin").click(function () {
        var num = Math.floor(Math.random() * 9000) + 1000;
        $("#pin").closest('.form-group').removeClass('is-empty').addClass('is-dirty');
        $("#pin").val(num);
    });

    //PROMO SMS TEMPLATE PAGE
    $(".promo_template_id").click(function () {
        $(".template_id").val($(this).val());
    });

    //PROMO SMS CUSATOMERS PAGE
    $("#selectAll").click(function () {
        $("input:checkbox:visible").prop('checked', this.checked);
    });

    //ALERT LIST
    $(".nfa_sms").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/accounts/profile/bentity/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , submit: 'nfa_sms'
                , id: $(this).attr('data-id')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    $(".nfa_email").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/accounts/profile/bentity/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , submit: 'nfa_email'
                , id: $(this).attr('data-id')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    $(".daily_report_sms").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/accounts/profile/bentity/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , submit: 'daily_report_sms'
                , id: $(this).attr('data-id')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

    $(".daily_report_email").click(function (event) {
        var status = false;
        if (this.checked) {
            status = true;
        }
        $.ajax({
            type: "POST"
            , url: "/accounts/profile/bentity/"
            , data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
                , submit: 'daily_report_email'
                , id: $(this).attr('data-id')
                , status: status
            }
        }).done(function (msg) {}).fail(function (msg) {
            return false;
        });
    });

});

//Generating CSRF Token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function makeDashChart(title, data_x_green, data_x_grey) {
    require(
        [
            'echarts', 'echarts/chart/line', 'echarts/chart/bar'
        ]
        , function (ec) {
            dashChart = ec.init(document.getElementById('dashChart'), 'macarons');
            var option = {
                title: {
                    text: title
                    , textStyle: {
                        color: '#3F51B5'
                    }
                    , subtext: 'No. of Hits'
                }
                , color: ['#3F51B5', '#434553']
                , tooltip: {
                    trigger: 'axis'
                }
                , legend: {
                    data: ['Happy', 'Unhappy']
                }
                , toolbox: {
                    show: true
                    , feature: {
                        magicType: {
                            show: true
                            , type: ['line', 'bar', 'stack', 'tiled']
                            , title: {
                                line: 'Line'
                                , bar: 'Bar'
                                , stack: 'Stack'
                                , tiled: 'Tiled'
                            }
                        }
                        , restore: {
                            show: true
                            , title: 'Restore'
                        }
                        , saveAsImage: {
                            show: true
                            , title: 'Save as Image'
                        }
                    }
                }
                , calculable: true
                , xAxis: [
                    {
                        type: 'category'
                        , boundaryGap: true
                        , axisLine: {
                            show: false
                        }
                        , axisTick: {
                            show: false
                        }
                        , data: tick_x
                    }
                ]
                , yAxis: [
                    {
                        axisLine: {
                            show: false
                        }
                        , axisTick: {
                            show: false
                        }
                        , type: 'value'
                    }
                ]
                , series: [
                    {
                        name: 'Unhappy'
                        , symbol: 'bar'
                        , symbolSize: 0
                        , lineStyle: {
                            width: 0
                        }
                        , borderColor: 'rgba(0,0,0,0)'
                        , type: 'bar'
                        , stack: 'A'
                        , itemStyle: {
                            normal: {
                                areaStyle: {
                                    type: 'default'
                                }
                            }
                        }
                        , data: data_x_grey
                    }, {
                        name: 'Happy'
                        , symbol: 'bar'
                        , symbolSize: 0
                        , lineStyle: {
                            width: 0
                        }
                        , type: 'bar'
                        , stack: 'A'
                        , itemStyle: {
                            normal: {
                                areaStyle: {
                                    type: 'default'
                                }
                            }
                        }
                        , data: data_x_green
                    }
                ]
            };

            dashChart.setOption(option);
            $(window).resize(function () {
                dashChart.resize();
            });
        }
    );
}

function makeRatingDashChart(data) {
    require(
        [
            'echarts', 'echarts/chart/line', 'echarts/chart/bar'
        ]
        , function (ec) {
            myChart = ec.init(document.getElementById('ratingDashChart'), 'macarons');
            var option = {
                tooltip: {
                    trigger: 'axis'
                }
                , legend: {
                    data: ['Ambience', 'Cost', 'Food', 'Service', 'Overall']
                }
                , toolbox: {
                    show: true
                    , feature: {
                        magicType: {
                            show: true
                            , type: ['line', 'bar', 'stack', 'tiled']
                            , title: {
                                line: 'Line'
                                , bar: 'Bar'
                                , stack: 'Stack'
                                , tiled: 'Tiled'
                            }
                        }
                        , restore: {
                            show: true
                            , title: 'Restore'
                        }
                        , saveAsImage: {
                            show: true
                            , title: 'Save as Image'
                        }
                    }
                }
                , calculable: true
                , xAxis: [
                    {
                        type: 'category'
                        , boundaryGap: true
                        , axisLine: {
                            show: false
                        }
                        , axisTick: {
                            show: false
                        }
                        , data: tick_x
                    }
                ]
                , yAxis: [
                    {
                        axisLine: {
                            show: false
                        }
                        , axisTick: {
                            show: false
                        }
                        , type: 'value'
                    }
                ]
                , series: [
                    {
                        name: 'Ambience'
                        , type: 'bar'
                        , symbolSize: 5
                        , itemStyle: {
                            normal: {
                                lineStyle: {
                                    width: 3
                                }
                            }
                        }
                        , data: data[0]
                    }, {
                        name: 'Cost'
                        , type: 'bar'
                        , symbolSize: 5
                        , itemStyle: {
                            normal: {
                                lineStyle: {
                                    width: 3
                                }
                            }
                        }
                        , data: data[1]
                    }, {
                        name: 'Food'
                        , type: 'bar'
                        , symbolSize: 5
                        , itemStyle: {
                            normal: {
                                lineStyle: {
                                    width: 3
                                }
                            }
                        }
                        , data: data[2]
                    }, {
                        name: 'Service'
                        , type: 'bar'
                        , symbolSize: 5
                        , itemStyle: {
                            normal: {
                                lineStyle: {
                                    width: 3
                                }
                            }
                        }
                        , data: data[3]
                    }, {
                        name: 'Overall'
                        , type: 'bar'
                        , symbolSize: 5
                        , itemStyle: {
                            normal: {
                                areaStyle: {
                                    type: 'default'
                                }
                                , lineStyle: {
                                    width: 3
                                }
                            }
                        }
                        , data: data[4]
                    }
                ]
            };

            myChart.setOption(option);
            $(window).resize(function () {
                myChart.resize();
            });
        }
    );
}

function setData(data) {
    backUpData = [];
    backUpData = data;
}

function doughnut_percent(val, max) {
    return (parseFloat((val / max) * 100).toFixed(1)) + '%';
}

function doughnut_color(val, max) {
    if (parseFloat(doughnut_percent(val, max)) > 50) {
        return "#3F51B5";
    } else {
        return "#434553";
    }
}

function makeDoughnutChart(element, data, nbFeedbacks) {
    var max = nbFeedbacks * 5;
    var labelTop = {
        normal: {
            label: {
                show: false
            }
            , labelLine: {
                show: false
            }
        }
    };
    var labelBottom = {
        normal: {
            color: '#EEE'
            , label: {
                show: true
                , position: 'center'
            }
            , labelLine: {
                show: false
            }
        }
        , emphasis: {
            color: 'rgba(0,0,0,0)'
        }
    };
    var radius = [53, 60];
    require(
        [
            'echarts', 'echarts/chart/pie'
        ]
        , function (ec) {
            var myChart = ec.init(document.getElementById(element), 'macarons');
            option = {
                series: [
                    {
                        type: 'pie'
                        , radius: radius
                        , itemStyle: {
                            normal: {
                                color: doughnut_color(data, max)
                                , label: {
                                    position: 'center'
                                    , formatter: function () {
                                        return doughnut_percent(data, max);
                                    }
                                    , textStyle: {
                                        fontSize: '25'
                                        , color: doughnut_color(data, max)
                                    }
                                }
                            }
                        }
                        , data: [{
                            value: data
                            , itemStyle: labelTop
                        }, {
                            value: max - data
                            , itemStyle: labelBottom
                        }]
                    }
                ]
            };
            myChart.setOption(option);
            $(window).resize(function () {
                myChart.resize();
            });
        }
    );
}

function loadDashboard(data) {
    setData(data);

    //Stat Boxes Values
    var nbFeedbacks = 0;
    var nbQD1 = 0;
    var nbQD2 = 0;
    var data_x_grey = [];
    var ansSet;
    tick_x = [];
    if (TIME_FILTER == 'WEEK' || TIME_FILTER == 'WEEKLY') {
        tick_x = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
    } else if (TIME_FILTER == 'YEAR' || TIME_FILTER == 'YEARLY') {
        tick_x = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
    } else {
        for (var i = 0; i < X_MAX; i++) {
            tick_x[i] = i;
        }
    }

    //FILLING JSON DATA
    if (TIME_FILTER === 'DAY') {
        makeDashChart("FEEDBACKS", data.feedback.day[1], data.feedback.day[0]);
        makeRatingDashChart(data.rating.day);
    } else if (TIME_FILTER === 'WEEK') {
        makeDashChart("FEEDBACKS", data.feedback.week[1], data.feedback.week[0]);
        makeRatingDashChart(data.rating.week);
    } else if (TIME_FILTER === 'MONTH') {
        makeDashChart("FEEDBACKS", data.feedback.month[1], data.feedback.month[0]);
        makeRatingDashChart(data.rating.month);
    } else if (TIME_FILTER === 'YEAR') {
        makeDashChart("FEEDBACKS", data.feedback.year[1], data.feedback.year[0]);
        makeRatingDashChart(data.rating.year);
    } else if (TIME_FILTER === 'DAILY') {
        makeDashChart("FEEDBACKS", data.feedback.daily[1], data.feedback.daily[0]);
        makeRatingDashChart(data.rating.daily);
    } else if (TIME_FILTER === 'WEEKLY') {
        makeDashChart("FEEDBACKS", data.feedback.weekly[1], data.feedback.weekly[0]);
        makeRatingDashChart(data.rating.weekly);
    } else if (TIME_FILTER === 'MONTHLY') {
        makeDashChart("FEEDBACKS", data.feedback.monthly[1], data.feedback.monthly[0]);
        makeRatingDashChart(data.rating.monthly);
    } else if (TIME_FILTER === 'YEARLY') {
        makeDashChart("FEEDBACKS", data.feedback.yearly[1], data.feedback.yearly[0]);
        makeRatingDashChart(data.rating.yearly);
    } else {
        makeDashChart("FEEDBACKS", data.feedback.monthly[1], data.feedback.monthly[0]);
        makeRatingDashChart(data.rating.monthly);
    }

    var nb_feedbacks = data.pie.nb_feedbacks;

    //DOUGHNUT CHARTS -----------------
    makeDoughnutChart('qs1Chart', data.pie.ratings[0], nb_feedbacks);
    makeDoughnutChart('qs2Chart', data.pie.ratings[1], nb_feedbacks);
    makeDoughnutChart('qs3Chart', data.pie.ratings[2], nb_feedbacks);
    makeDoughnutChart('qs4Chart', data.pie.ratings[3], nb_feedbacks);
    makeDoughnutChart('qd1Chart', data.pie.ratings[4], data.pie.nb_qd1);
    makeDoughnutChart('qd2Chart', data.pie.ratings[5], data.pie.nb_qd2);
}

function loadEmployeeChart(data) {
    setData(data);

    //Stat Boxes Values
    var nbFeedbacks = 0;
    var nbQD1 = 0;
    var nbQD2 = 0;
    var data_x_grey = [];
    var ansSet;
    tick_x = [];
    if (TIME_FILTER == 'WEEK' || TIME_FILTER == 'WEEKLY') {
        tick_x = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
    } else if (TIME_FILTER == 'YEAR' || TIME_FILTER == 'YEARLY') {
        tick_x = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
    } else {
        for (var i = 0; i < X_MAX; i++) {
            tick_x[i] = i;
        }
    }

    //FILLING JSON DATA
    if (TIME_FILTER === 'DAY') {
        makeDashChart("EMPLOYEE", data.feedback.day[1], data.feedback.day[0]);
    } else if (TIME_FILTER === 'WEEK') {
        makeDashChart("EMPLOYEE", data.feedback.week[1], data.feedback.week[0]);
    } else if (TIME_FILTER === 'MONTH') {
        makeDashChart("EMPLOYEE", data.feedback.month[1], data.feedback.month[0]);
    } else if (TIME_FILTER === 'YEAR') {
        makeDashChart("EMPLOYEE", data.feedback.year[1], data.feedback.year[0]);
    } else if (TIME_FILTER === 'DAILY') {
        makeDashChart("EMPLOYEE", data.feedback.daily[1], data.feedback.daily[0]);
    } else if (TIME_FILTER === 'WEEKLY') {
        makeDashChart("EMPLOYEE", data.feedback.weekly[1], data.feedback.weekly[0]);
    } else if (TIME_FILTER === 'MONTHLY') {
        makeDashChart("EMPLOYEE", data.feedback.monthly[1], data.feedback.monthly[0]);
    } else if (TIME_FILTER === 'YEARLY') {
        makeDashChart("EMPLOYEE", data.feedback.yearly[1], data.feedback.yearly[0]);
    } else {
        makeDashChart("EMPLOYEE", data.feedback.monthly[1], data.feedback.monthly[0]);
    }
}

// ////////////////////////////////////////////////////////
// OWNER DASHBOARD ////////////////////////////////////////
// ////////////////////////////////////////////////////////
function loadDashboardOwner(data) {
    setData(data);

    //Stat Boxes Values
    var nbFeedbacks = 0;
    var nbQD1 = 0;
    var nbQD2 = 0;
    var data_x_grey = [];
    var ansSet;
    tick_x = data.names;
    console.log(tick_x);

    //FILLING JSON DATA
    if (TIME_FILTER === 'DAY') {
        makeDashChart("FEEDBACKS", data.greens.today, data.greys.today);
    } else if (TIME_FILTER === 'WEEK') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else if (TIME_FILTER === 'MONTH') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else if (TIME_FILTER === 'YEAR') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else if (TIME_FILTER === 'DAILY') {
        makeDashChart("FEEDBACKS", data.greens.today, data.greys.today);
    } else if (TIME_FILTER === 'WEEKLY') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else if (TIME_FILTER === 'MONTHLY') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else if (TIME_FILTER === 'YEARLY') {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    } else {
        makeDashChart("FEEDBACKS", data.greens.all, data.greys.all);
    }
}