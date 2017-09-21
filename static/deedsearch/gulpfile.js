// include gulp and required plugins
var gulp = require('gulp');
var sass = require('gulp-sass');
var browserSync = require('browser-sync');
var notify = require('gulp-notify');
//var cp = require('child_process');

gulp.task('compile-sass', function () {
    var loadPaths = [
        'bower_components/bourbon/dist',
        'bower_components/bourbon/app/assets/stylesheets',
        'bower_components/bootstrap-sass-official/vendor/assets/stylesheets',
        'bower_components/neat/app/assets/stylesheets/neat'
    ]

    return gulp.src('sass/**/*.scss')
        .pipe(sass({ loadPath: loadPaths, sourcemap: true, style: 'compressed'}))
        .on('error', notify.onError(function (error) {
            return 'Dang! ' + error.message;
        }))
        .pipe(gulp.dest('css'))
        .pipe(gulp.dest('css'))
        .pipe(browserSync.stream());
});

gulp.task('browser-sync', ['compile-sass'], function() {  
    browserSync.init(['css/*.css'], {
        open: false,
        proxy: 'localhost:8000'
    });
});

gulp.task('watch', function() {
    gulp.watch(['sass/**/*.scss'], ['compile-sass']);
    gulp.watch(['../../**/*.html', '**/*.py']).on('change', browserSync.reload);
});

// watch for changes
gulp.task('default', ['compile-sass']);
gulp.task('develop', ['compile-sass', 'browser-sync', 'watch']);
