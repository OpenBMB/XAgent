import type { Directive, App } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const highlightDirective: Directive = {
  mounted: function bind(el, binding) {
    // on first bind, highlight all targets
    const targets = el.querySelectorAll('code')
    let target
    let i

    for (i = 0; i < targets.length; i += 1) {
      target = targets[i]

      if (typeof binding.value === 'string') {
        // if a value is directly assigned to the directive, use this
        // instead of the element content.
        target.textContent = binding.value
      }

      hljs.highlightBlock(target)
    }
  },
  updated: function componentUpdated(el, binding) {
    // after an update, re-fill the content and then highlight
    const targets = el.querySelectorAll('code')
    let target
    let i

    for (i = 0; i < targets.length; i += 1) {
      target = targets[i]
      if (typeof binding.value === 'string') {
        target.textContent = binding.value
        hljs.highlightBlock(target)
      }
    }
  },
}

export function setupHighlightDirective(app: App) {
  app.directive('hljs', highlightDirective)
}

export default highlightDirective
