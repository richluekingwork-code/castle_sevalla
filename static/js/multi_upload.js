/**
 * multi_upload.js
 * Enables multiple-file selection on ProjectImage inline upload inputs.
 * Loaded via ProjectsAdmin.Media.js in admin.py.
 */
(function ($) {
    "use strict";

    function enableMultiUpload() {
        // Target every file input inside the ProjectImage inline
        $('input[type="file"]', '.inline-group').each(function () {
            $(this).attr('multiple', 'multiple');
        });
    }

    $(document).ready(function () {
        enableMultiUpload();

        // Re-run after Django's inline "Add another" button adds a new row
        $(document).on('formset:added', function (event, $row) {
            $('input[type="file"]', $row).attr('multiple', 'multiple');
        });
    });
}(django.jQuery));
