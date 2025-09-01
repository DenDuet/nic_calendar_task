
$(window).on("load", function () {



  function ride() {
    /*=== Draggable Box ===*/
    $(".resize").draggable({
      axis: "x,y",
      animate: true,
      grid: [102, 91],
      containment: '.grids-body',
      scroll: true,
      revert: "valid",
      refreshPositions: true,
      start: function (event, ui) {
      },
      stop: function (event, ui) {

      } });


    /*=== Droppable ===*/
    $(".ride").droppable({
      tolerance: "touch" });



    var targetPos = [];
    var sp = "";
    /*=== Resizable Box ===*/
    $(".resize").resizable({
      grid: [102, 0],
      animate: false,
      handles: 'e',
      containment: '.grids-body',
      maxHeight: 77,
      minHeight: 77,
      start: function (event, ui) {
        targetPos = [];
        $('.ride').each(function () {
          targetPos.push($(this).position());
        });
        sp = ui.position.left + ui.size.width;
      },
      stop: function (event, ui) {
        var ep = ui.position.left + ui.size.width;
        var tp = ui.position.top;
        $.each(targetPos, function (i, e) {
          if (targetPos[i].top == tp) {
            if (targetPos[i].left > sp && targetPos[i].left < ep) {
              ui.element.css(ui.originalSize);
              setTimeout(function () {
                detectShortRides();
              }, 100);
            }
          }
        });

      } });




    $(".resize").on("resizestop", function (event, ui) {
      if (ui.size.width <= 204) {
        $(this).addClass("short-ride");
      } else
      {
        $(this).removeClass("short-ride");
      }
      setTimeout(function () {
        RideTime(ui.element[0]);
      }, 400);
    });


    function detectShortRides() {
      $(".ride").each(function () {
        if ($(this).width() <= 204) {
          $(this).addClass("short-ride");
        } else
        {
          $(this).removeClass("short-ride");
        }
      });
    }
    detectShortRides();


    $(".show-add").on("click", function () {
      $(this).parents('.ride').find('.complete-add').fadeIn();
    });

    $(".complete-add").on("click", function () {
      $(this).fadeOut();
    });
  }
  ride();

  /*=== New Ride Menu ===*/
  $("html").on("click", function (event) {
    if ($(event.target).is(".grids-body .timeslot")) {
      $("#add-ride .modal-title h4").text('New Ride');
      $("#pass-name").val("");
      $("#pass-contact").val("");
      $("#pass-loc").val("");
      $("#add-ride .add-ride-btn").show();
      $("#add-ride .edit-ride-btn").hide();

      $(".ride-opts").removeClass("show");
      $(".new-ride").addClass("show");
      let left = $(event.target).offset().left;
      let top = $(event.target).offset().top;
      $(".new-ride").css({
        "left": left + 50,
        "top": top + 30 });

    } else
    {
      $(".ride-opts").removeClass("show");
      $(".new-ride").removeClass("show");
      $(".new-ride").css({
        "left": 0,
        "top": 0 });

    }
  });

  /*=== Menu On Right For Edit Or Delete A Ride ===*/
  document.oncontextmenu = function () {return false;};
  $("body").on("mousedown", ".grids-body .ride", function (e) {
    if (e.button == 2) {
      $(".new-ride").removeClass("show");
      $(".ride").removeClass("selected");
      $(this).addClass("selected");
      $(".ride-opts").addClass("show");
      let left = $(this).offset().left;
      let top = $(this).offset().top;
      $(".ride-opts").css({
        "left": left + 50,
        "top": top + 30 });

      return false;
    }
    return true;
  });

  /*=== Delete Ride ===*/
  $(".delete-ride").on("click", function () {
    $(".ride.selected").detach();
  });

  /*=== Edit Ride Popup Open ===*/
  $(".edit-ride").on("click", function () {
    if ($(".ride.selected").hasClass('maintenance') || $(".ride.selected").hasClass('preparation') || $(".ride.selected").hasClass('return') || $(".ride.selected").hasClass('service')) {
      $("#change-ride").modal('show');
      $('.change-ride').val('service').trigger('change');
    } else
    {
      $("#add-new").modal('show');
      let name = $(".ride.selected .passenger-info .pass-name").text();
      let contact = $(".ride.selected .passenger-info .pass-contact").text();
      let loc = $(".ride.selected .passenger-info .pass-loc").text();
      $("#add-ride #pass-name").val(name);
      $("#add-ride #pass-contact").val(contact);
      $("#add-ride #pass-loc").val(loc);
      $("#add-ride .modal-title h4").text('Edit Ride');
      $("#add-ride .add-ride-btn").hide();
      $("#add-ride .edit-ride-btn").show();
    }
  });



  /*=== Ride Changer ===*/
  $("#ride-changer").submit(function () {
    let changedRide = $('.change-ride').select2('data')[0].element.value;
    let rideName = $('.change-ride').select2('data')[0].text;
    $(".ride.selected .other-info span").html(rideName);
    if (rideName == 'Return') {
      $(".ride.selected .other-info i").attr('class', 'ion-arrow-return-left');
    }
    if (rideName == 'Maintenance') {
      $(".ride.selected .other-info i").attr('class', 'ion-settings');
    }
    if (rideName == 'Preparation') {
      $(".ride.selected .other-info i").attr('class', 'ion-pinpoint');
    }
    if (rideName == 'Service') {
      $(".ride.selected .other-info i").attr('class', 'ion-pull-request');
    }
    $(".ride.selected").attr('class', "ride resize butNotHere " + changedRide);
    $("#change-ride").modal('hide');
    return false;
  });

  /*=== New Ride Menu Open Position ===*/
  var myposleft;
  var mypostop;
  $(".timeslot").on("click", function () {
    myposleft = $(this).offset().left - $(".grids-body").offset().left - 1;
    mypostop = $(this).offset().top - $(".grids-body").offset().top + 2;
  });

  /*=== Add New Ride On Submit Popup Form ===*/
  $('#add-ride').submit(function () {
    // Get Values Filled in the Form
    let name = $("#pass-name").val();
    let contact = $("#pass-contact").val();
    let date = $("#pass-date").val();
    let loc = $("#pass-loc").val();
    // If New Ride
    if ($(".custom-btn:focus").hasClass("add-ride-btn")) {
      $(".grids-body").prepend(`
		            <div class="ride resize butNotHere" style="left:${myposleft}px; top:${mypostop}px">
		                <div class="passenger-info complete-add scrolly">
		                    <ul>
		                        <li><i class="ion-ios-location-outline"></i>${loc}</li>
		                    </ul>
		                </div>
		                <div class="passenger-info scrolly">
		                    <ul>
								<li><i class="ion-android-person"></i> <strong class="pass-name">${name}</strong></li>
								<li><i class="ion-ios-telephone-outline"></i> <span class="pass-contact">${contact}</span></li>
								<li><a class="show-add" href="#" title=""> <i class="ion-ios-location-outline"></i> <span class="pass-loc"> ${loc}</span></a></li>
		                    </ul>
		                </div>
		                <div class="assign-driver">
		                    <span>Driver Not Assigned</span>
		                    <a class="custom-btn" data-toggle="modal" data-target="#assign-driver"  href="#" title=""><i class="ion-android-person-add"></i> Assign Driver</a>
		                </div>
						<div class="short-ride-info">
							<ul>
								<li><i class="ion-android-person"></i> <strong class="pass-name">${name}</strong></li>
								<li><i class="ion-ios-telephone-outline"></i> <span class="pass-contact">${contact}</span></li>
								<li><a class="show-add" href="#" title=""> <i class="ion-ios-location-outline"></i> <span  class="pass-loc">${loc}</span></a></li>
							</ul>
						</div>
		            </div>
		        `);
      ride();
      customScroll();

      $("#add-new").modal('hide');
      return false;
    }
    // If Edit Ride
    else if ($(".custom-btn:focus").hasClass("edit-ride-btn")) {
        $(".ride.selected .pass-name").text(name);
        $(".ride.selected .pass-contact").text(contact);
        $(".ride.selected .pass-loc").text(loc);

        $(".ride.selected").removeClass('selected');
        $("#pass-name").val("");
        $("#pass-contact").val("");
        $("#pass-loc").val("");
        $("#add-new").modal('hide');
        $("#add-ride .edit-ride-btn").hide();
        $("#add-ride .add-ride-btn").show();
        $("#add-ride .modal-title h4").text('New Ride');
        return false;
      }
  });

  /*=== Ride Cancel ===*/
  $(".ride-cancel").on("click", function () {
    $(".ride.selected").removeClass('selected');
    $("#pass-name").val("");
    $("#pass-contact").val("");
    $("#pass-loc").val("");
    $("#add-new").modal('hide');
  });


  /*=== Return To Base ===*/
  $(".other-info-btn").on("click", function () {
    let iconClass = $(this).find('i').attr("class");
    let text = $(this).find('span').text();
    let rideClass = $(this).attr('data-rideclass');
    $(".grids-body").prepend(`
				<div class="ride resize butNotHere ${rideClass}" style="left:${myposleft}px; top:${mypostop}px">
					<div class="other-info">
						<i class="${iconClass}"></i>
						<span>${text}</span>
					</div>
				</div>`);
    ride();
    $(".new-ride").removeClass("show");
    return false;
  });



  /*=== Select Ride To Assign Driver ===*/
  $('body').on("click", 'a[data-target="#assign-driver"]', function () {
    $(this).parents('.ride').addClass('assign-to-me');
    $(".driver-selector tr").removeClass('selected');
  });


  $("body").on("click", ".driver-selector tr", function () {
    $(this).addClass('selected').siblings().removeClass('selected');
  });

  /*=== Select Driver ===*/
  $("#select-driver").submit(function () {
    // let selectedDriver = $('.all-driver').select2('data')[0].text;
    // let selectedDriver = $("#new-driver").val();
    // let driverImage = $(".inputpicker-wrapped-list .table>tbody>tr>td img").attr('src');
    let selectedDriver = $(".driver-selector tr.selected td.console-driver").text();
    let driverImage = $(".driver-selector tr.selected td.console-driver-img img").attr('src');
    $(".assign-to-me .assign-driver").detach();
    $(".assign-to-me").append(`
			<div class="driver-info">
				<ul>
					<li><img src="${driverImage}"> <i class="ion-android-person"></i> <strong class="driver-name">${selectedDriver}</strong></li>
					<li><i class="ion-ios-clock-outline"></i> <span><i class="hr">02</i>:<i class="mins">02</i>Hours</span></li>
				</ul>
			</div>`);

    RideTime(".assign-to-me");

    $(".assign-to-me").addClass('assigned').removeClass('assign-to-me');

    if ($('.ride').hasClass('change-driver')) {
      $(".change-driver .driver-info .driver-name").html(selectedDriver);
      $(".change-driver .driver-info ul li img").attr('src', driverImage);
      $(".change-driver").removeClass('change-driver');
      $("#assign-driver .modal-header .modal-title h4").text('Assign A Driver');
    }

    $("#assign-driver").modal('hide');
    return false;
  });


  /*=== Cancel Popup ===*/
  $(".cancel-popup").on("click", function () {
    $(".change-driver").removeClass('change-driver');
  });


  /*=== Change Driver ===*/
  $("body").on("click", ".driver-info", function () {
    $(this).parents('.ride').addClass('change-driver');
    let thisDriver = $(this).find('.driver-name').text();
    $("#assign-driver .modal-header .modal-title h4").text('Change The Driver');
    $("#assign-driver").modal('show');
    $(".driver-selector tr").removeClass('selected');
    console.log($(`td[drivername='${thisDriver}']`));
    $("td[drivername='" + thisDriver + "']").parents('tr').addClass('selected');
  });


  /* ===  Add Short Ride Info To Each Ride === */
  $(".ride").each(function () {
    if ($(this).hasClass('return') || $(this).hasClass('maintenance') || $(this).hasClass('preparation') || $(this).hasClass('service')) {
      return true;
    } else
    {
      // Add Short Ride Info To Each Ride
      let name = $(this).find(".passenger-info .pass-name").text();
      let contact = $(this).find(".passenger-info .pass-contact").text();
      let loc = $(this).find(".passenger-info .pass-loc").text();
      $(this).append(`<div class="short-ride-info">
					<ul>
						<li><i class="ion-android-person"></i> <strong class="pass-name">${name}</strong></li>
						<li><i class="ion-ios-telephone-outline"></i> <span  class="pass-contact">${contact}</span></li>
						<li><i class="ion-ios-location-outline"></i> <span class="pass-loc">${loc}</span></li>
					</ul>
				</div>`);
      RideTime(this);
    }
  });


  // Update Driver Time For the Assigned Drive
  function RideTime(thisRide) {
    let rideWidth = $(thisRide).width();
    let updateTime = convertPixelToTime(rideWidth);

    function pad2(number) {
      return (number < 10 ? '0' : '') + number;
    }



    $(thisRide).find(".driver-info .hr").text(pad2(updateTime.h));
    $(thisRide).find(".driver-info .mins").text(pad2(updateTime.m));
  }




  /* ===  Convert Mili Seconds Hours === */
  function convertMiliseconds(miliseconds, format) {
    var days, hours, minutes, seconds, total_hours, total_minutes, total_seconds;

    total_seconds = parseInt(Math.floor(miliseconds / 1000));
    total_minutes = parseInt(Math.floor(total_seconds / 60));
    total_hours = parseInt(Math.floor(total_minutes / 60));
    days = parseInt(Math.floor(total_hours / 24));

    seconds = parseInt(total_seconds % 60);
    minutes = parseInt(total_minutes % 60);
    hours = parseInt(total_hours % 24);

    switch (format) {
      case 's':
        return total_seconds;
        break;
      case 'm':
        return total_minutes;
        break;
      case 'h':
        return total_hours;
        break;
      case 'd':
        return days;
        break;
      default:
        return { d: days, h: hours, m: minutes, s: seconds };
      //return { h: hours, m: minutes}
    }
  };

  function convertPixelToTime(pixels) {
    let onePx = 17647.05882352941;
    return convertMiliseconds(pixels * onePx);
  }


  setTimeout(function () {
    $(".xdsoft_today").trigger('click');
  }, 1000);


  /* === Date Time Picker == */
  jQuery('.new-datepicker').datetimepicker({
    validateOnBlur: false,
    timepicker: false,
    //format:'D, M d,Y',
    format: 'M-d-Y',
    value: new Date(),
    defaultDate: false,
    onSelectDate: function (dp, $input) {
    } });


  jQuery('.datetimepicker').datetimepicker({
    validateOnBlur: false,
    format: 'm-d-Y h:i A',
    value: new Date() });


  jQuery('.timepicker').datetimepicker({
    validateOnBlur: false,
    datepicker: false,
    format: 'h:i A',
    value: new Date() });




  var month = new Array();
  month[0] = "Jan";
  month[1] = "Feb";
  month[2] = "Mar";
  month[3] = "Apr";
  month[4] = "May";
  month[5] = "Jun";
  month[6] = "Jul";
  month[7] = "Aug";
  month[8] = "Sep";
  month[9] = "Oct";
  month[10] = "Nov";
  month[11] = "Dec";


  $(".nextDate").on("click", function () {
    let a = $(".new-datepicker").val();
    let newDate = new Date(new Date(a).getTime() + 1 * 24 * 60 * 60 * 1000);
    let date = newDate.getDate();
    let tempMonth = month[newDate.getMonth()];
    let year = newDate.getFullYear();
    console.log(newDate);
    $(".new-datepicker").val(tempMonth + "-" + date + "-" + year);
    return false;
  });

  $(".prevDate").on("click", function () {
    let a = $(".new-datepicker").val();
    let newDate = new Date(new Date(a).getTime() - 1 * 24 * 60 * 60 * 1000);
    let date = newDate.getDate();
    let tempMonth = month[newDate.getMonth()];
    let year = newDate.getFullYear();
    console.log(newDate);
    $(".new-datepicker").val(tempMonth + "-" + date + "-" + year);
    return false;
  });

  /*=== Select2 ===*/
  $('.select,.bottom select').select2({
    placeholder: 'Select an option' });


  customScroll();

});


function customScroll() {
  $(".scrolly").mCustomScrollbar({
    axis: "y",
    theme: "light-3",
    scrollbarPosition: "outside" });


}