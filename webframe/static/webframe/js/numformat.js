/**
 * File:   webframe/static/js/numformat.js
 * Author: Kenson Man <kenson.idv.hk@gmail.com>
 * Date:   2019-04-20 11:04
 * Desc:   Provide the method "format" to format number.
 * Example:
 *    123456.789.format()                 => 123,456.79
 *    123456.789.format(2, '*', '#')      => 123#456*79
 * Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/NumberFormat
 */
Number.prototype.format=function(c) {
   return new Intl.NumberFormat('en-US', {style:"decimal", maximumFractionDigits:c}).format(this);
}
