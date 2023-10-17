module.exports = {
  ignores: [(commit) => commit.includes('init')],
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [1, 'always'],
    'header-max-length': [2, 'always', 108],
    'subject-empty': [2, 'never'],
    'type-empty': [2, 'never'],
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'chore', 'style', 'refactor', 'ci', 'test', 'revert', 'perf', 'build', 'vercel'],
      // ① build：对构建系统或者外部依赖项进行了修改
      // ② ci：对CI配置文件或脚本进行了修改
      // ③ docs：对文档进行了修改
      // ④ feat：增加新的特征
      // ⑤ fix：修复bug
      // ⑥ pref：提高性能的代码更改
      // ⑦ refactor：既不是修复bug也不是添加特征的代码重构
      // ⑧ style：不影响代码含义的修改，比如空格、格式化、缺失的分号等
      // ⑨ test：增加确实的测试或者矫正已存在的测试
    ],
  },
}
