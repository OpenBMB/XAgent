
// const generateSensitiveMap = (wordList: string[]): any => {
//   const sensitiveMap = new Map()

//   for (let i = 0, len = wordList.length; i < len; ++i) {
//     let map = sensitiveMap
//     const word = wordList[i]
//     for (let j = 0; j < word.length; ++j) {
//       const ch = word.charAt(j)
//       if (map.get(ch)) {
//         map = map.get(ch)
//         if (map.get('isEnd') === true) {
//           break
//         }
//       } else {
//         if (map.get('isEnd') === true) {
//           map.set('isEnd', false)
//         }
//         const nextMap = new Map()
//         nextMap.set('isEnd', true)
//         map.set(ch, nextMap)
//         map = nextMap
//       }
//     }
//   }
//   return sensitiveMap
// }

// const sensitiveMap = generateSensitiveMap(sensitive)
// const checkSensitiveIsExist = (txt: string, index: number): { flag: boolean; sensitiveWord: string } => {
//   let flag = false
//   let sensitiveWord = ''
//   let wordNum = 0
//   let currentMap = sensitiveMap
//   for (let i = index; i < txt.length; i++) {
//     const word = txt.charAt(i)
//     currentMap = currentMap.get(word)
//     if (currentMap) {
//       wordNum++
//       sensitiveWord += word
//       if (currentMap.get('isEnd') === true) {
//         flag = true
//         break
//       }
//     } else {
//       break
//     }
//   }
//   if (wordNum < 2) {
//     flag = false
//   }
//   return { flag, sensitiveWord }
// }

// export const useIsExistSensitive = (str: string) => {
//   let matchResult = { flag: false, sensitiveWord: '' }
//   const strTrim = str.replace(/[^\u4e00-\u9fa5\u0030-\u0039\u0061-\u007a\u0041-\u005a]+/g, '')
//   for (let i = 0; i < strTrim.length; i++) {
//     matchResult = checkSensitiveIsExist(strTrim, i)
//     if (matchResult.flag) return true
//   }
//   return matchResult.flag
// }


export const useIsExistSensitive = (str: string) => ({});