module.exports = (ctx) => ({
    map: ctx.options.map,
    parser: ctx.options.parser,
    plugins: {
        '@csstools/postcss-oklab-function': {'preserve': true},
    },
})