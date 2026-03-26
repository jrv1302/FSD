$(document).ready(function () {

  setTimeout(function () {
    $('#flash-container .alert').fadeOut(500, function () { $(this).remove(); });
  }, 4000);

  $(document).on('click', '.toggle-pw', function () {
    const targetId = $(this).data('target');
    const input    = $('#' + targetId);
    const icon     = $(this).find('i');
    if (input.attr('type') === 'password') {
      input.attr('type', 'text');
      icon.removeClass('bi-eye').addClass('bi-eye-slash');
    } else {
      input.attr('type', 'password');
      icon.removeClass('bi-eye-slash').addClass('bi-eye');
    }
  });

  $('#regPw').on('input', function () {
    const pw  = $(this).val();
    const bar = $('#pwStrengthBar');
    const seg = $('#strengthBar');
    const lbl = $('#strengthLabel');

    if (!pw.length) { bar.hide(); return; }
    bar.show();

    let score = 0;
    if (pw.length >= 6)  score++;
    if (pw.length >= 10) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;

    const levels = [
      { label: 'Very Weak', cls: 'bg-danger',  w: 20 },
      { label: 'Weak',      cls: 'bg-warning', w: 40 },
      { label: 'Fair',      cls: 'bg-info',    w: 60 },
      { label: 'Strong',    cls: 'bg-primary', w: 80 },
      { label: 'Very Strong', cls: 'bg-success', w: 100 },
    ];
    const lvl = levels[Math.min(score - 1, 4)] || levels[0];
    seg.css('width', lvl.w + '%')
       .removeClass('bg-danger bg-warning bg-info bg-primary bg-success')
       .addClass(lvl.cls);
    lbl.text(lvl.label);
  });

  $('#registerForm').on('submit', function (e) {
    let valid = true;

    const name = $('[name="name"]').val().trim();
    if (!name) {
      $('[name="name"]').addClass('is-invalid');
      valid = false;
    } else {
      $('[name="name"]').removeClass('is-invalid').addClass('is-valid');
    }

    const email = $('[name="email"]').val().trim();
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRe.test(email)) {
      $('[name="email"]').addClass('is-invalid');
      valid = false;
    } else {
      $('[name="email"]').removeClass('is-invalid').addClass('is-valid');
    }

    const pw = $('#regPw').val();
    if (pw.length < 6) {
      $('#regPw').addClass('is-invalid');
      valid = false;
    } else {
      $('#regPw').removeClass('is-invalid').addClass('is-valid');
    }

    const cpw = $('#confirmPw').val();
    if (pw !== cpw) {
      $('#confirmPw').addClass('is-invalid');
      $('#confirmErr').text('Passwords do not match.');
      valid = false;
    } else {
      $('#confirmPw').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) e.preventDefault();
  });

  $('#loginForm').on('submit', function (e) {
    let valid = true;
    const email = $('[name="email"]').val().trim();
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRe.test(email)) {
      $('[name="email"]').addClass('is-invalid');
      valid = false;
    } else {
      $('[name="email"]').removeClass('is-invalid');
    }

    if (!$('[name="password"]').val()) {
      $('[name="password"]').addClass('is-invalid');
      valid = false;
    } else {
      $('[name="password"]').removeClass('is-invalid');
    }

    if (!valid) e.preventDefault();
  });

  $('#complaintForm').on('submit', function (e) {
    let valid = true;

    const title = $('#complaintTitle').val().trim();
    if (!title) {
      $('#complaintTitle').addClass('is-invalid');
      valid = false;
    } else {
      $('#complaintTitle').removeClass('is-invalid').addClass('is-valid');
    }

    const desc = $('#complaintDesc').val().trim();
    if (desc.length < 20) {
      $('#complaintDesc').addClass('is-invalid');
      valid = false;
    } else {
      $('#complaintDesc').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) {
      e.preventDefault();
      $('html, body').animate({ scrollTop: 0 }, 300);
    } else {
      const btn = $('#submitBtn');
      btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Classifying…');
    }
  });

  $('#complaintTitle').on('input', function () {
    $('#titleCount').text($(this).val().length);
  });
  $('#complaintDesc').on('input', function () {
    $('#descCount').text($(this).val().length);
  });

  $('input, textarea').on('input', function () {
    $(this).removeClass('is-invalid');
  });

});