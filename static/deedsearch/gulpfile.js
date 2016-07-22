// include gulp and required plugins
var gulp = require('gulp');
var sass = require('gulp-sass');
var browserSync = require('browser-sync');
//var notify = require('gulp-notify');
//var imagemin = require('gulp-imagemin');
//var pngcrush = require('imagemin-pngcrush');
//var cp = require('child_process');

var messages = {
    jekyllBuild: '<span style="color: grey">Running:</span> $ jekyll build'
};


// build the jekyll site
/*
gulp.task('jekyll-build', function (done) {
    browserSync.notify(messages.jekyllBuild);
    return cp.spawn('jekyll', ['build'], {stdio: 'inherit'})
        .on('close', done);
});
*/

// rebuild jekyll and do page reload
/*
gulp.task('jekyll-rebuild', ['jekyll-build'], function () {
    browserSync.reload();
});
*/

// compile sass into both _site/assets/css (for live injecting) and site (for future jekyll builds)
gulp.task('compile-sass', function () {
    var loadPaths = [
        'bower_components/bourbon/dist',
        'bower_components/bourbon/app/assets/stylesheets',
        'bower_components/bootstrap-sass-official/vendor/assets/stylesheets',
        'bower_components/neat/app/assets/stylesheets/neat'
    ]

    return gulp.src('sass/**/*.scss')
        .pipe(sass({ loadPath: loadPaths, sourcemap: true, style: 'compressed'}))
        /*.on("error", notify.onError(function (error) {
            return "Dang! " + error.message;
        }))*/
        .pipe(gulp.dest('css'))
        .pipe(gulp.dest('_site/css'));
});

// minify PNG, JPEG, GIF and SVG images
gulp.task('imagemin', function () {
    return gulp.src('img/**/*')
        .pipe(imagemin({
            progressive: true,
            svgoPlugins: [{removeViewBox: false}],
            use: [pngcrush()]
        }))
        .pipe(gulp.dest('img/'))
        .pipe(gulp.dest('_site/img/'));
});

// start a server and watch for html and css changes
gulp.task('browser-sync', ['compile-sass'], function() {  
    browserSync.init(['_site/css/*.css'], {
        server: {
            baseDir: '_site'
        }
    });
});

// watch for changes
gulp.task('default', ['compile-sass']);
gulp.task('default', ['compile-sass', 'browser-sync'], function () {  
    gulp.watch(['sass/**/*.scss'], ['compile-sass']);
//    gulp.watch(['img/**/*'], ['imagemin']);
//    gulp.watch([ '*.yml', '*.md', '*.html', '_includes/*.html', '_layouts/*.html'], ['jekyll-rebuild']);
});
