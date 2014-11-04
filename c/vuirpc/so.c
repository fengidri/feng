/**
 *   author       :   丁雪峰
 *   time         :   2014-10-18 09:56:18
 *   email        :   fengidri@yeah.net
 *   version      :   1.0.1
 *   description  :
 */
#include <stdio.h>
#include <stddef.h>
#include <unistd.h>
#include <stdbool.h>
#include <malloc.h>
#include <string.h>

const char * strstrcase(const char *src, size_t  len, 
        const char *pat, size_t size)
{
    size_t offset;
    size_t f;
    int tmp;
    const char *p;
    f = 0;
    do{
        p = pat;
        offset = 0;
        do{
            tmp = *p - *(src + offset);
            if(0 != tmp && 32 != tmp) break;
            ++offset;
            ++p;
            if (offset >= size) return src;
        }while(1);
        ++f;
    }while(f < len);
    return NULL;
}



// 用于描述在 match_key 的返回结果集中的一个元素. 
struct so_matched{
    const char *s;  // 
    size_t len;     // 元素长度
    bool match;     // 是否合符
    size_t index;   // 结果集中的id
    const char *p;  // 对应的pat
};
struct so_setmatched{
    size_t size;
    size_t totle;
    struct so_matched elements[];
};


/**
 * match_key -- 依据patten 在string 中查找合符的子字符
 * @string:   源字符串
 * @patten:   模式
 * @res:      OUT 用于返回结果
 * @m:        IN res 的大小 OUT 实际的大小.
 */
bool match_key(const char *string, const char *patten, 
        struct so_setmatched **res)
{
    size_t index, ss, curindex, i;
    const char *start, *target, *pos;
    struct so_setmatched *set;

    pos = patten;
    index = 0;

    while(1)
    {
        while(' ' == *pos && 0 != *pos) pos ++;
        if (0 == *pos) break;
        ++ index;
        // 跳过一般字符
        while (' ' != *pos && 0 != *pos) pos ++;
    }
    set = (struct so_setmatched *)malloc(sizeof(struct so_setmatched) + 
            sizeof(struct so_matched) * index);
    set->totle = index;
    set->elements[0].s = string;
    set->elements[0].len = strlen(string);
    set->elements[0].match = false;

    pos = patten;
    index = 0;
    while(1){// 首先分割patten
        // 跳过空格
        while(' ' == *pos && 0 != *pos) pos ++;
        if (0 == *pos) break;
        start = pos;
        // 跳过一般字符
        while (' ' != *pos && 0 != *pos) pos ++;

        ss = pos - start;

        // 在最后一个结果集中找 
        target = strstrcase((set->elements + index)->s, 
                (set->elements + index)->len,
                start, ss);
        curindex = index;
        if (NULL == target) {
            for (i = 0; i < index - 1; ++i)
            {
                if((set->elements + i)->match) continue;
                target = strstrcase((set->elements + i)->s, 
                        (set->elements + i)->len,
                        start, ss);
                curindex = i;
            }
        }
        if (NULL == target) continue;

        if (ss == (set->elements + curindex)->len)// 全等
        {
            (set->elements + curindex)->match = true;
            (set->elements + curindex)->p = start;

        }
        else if (target == (set->elements + curindex)->s)// 头对齐
        {
            memmove(set->elements + curindex, set->elements + curindex + 1,
                    sizeof(set->elements[0]) * (index - curindex));

            (set->elements + curindex + 1)->match = false;
            (set->elements + curindex + 1)->len = (set->elements + curindex)->len - ss;
            (set->elements + curindex + 1)->s = (set->elements + curindex)->s + ss;

            (set->elements + curindex)->match = true;
            (set->elements + curindex)->len -= ss;
            (set->elements + curindex)->p = start;
        }
        else if (target + ss == (set->elements + curindex)->s + (set->elements + curindex)->len)//尾对齐
        {
            memmove(set->elements + curindex, set->elements + curindex + 1,
                    sizeof(set->elements[0]) * (index - curindex));
            (set->elements + curindex + 1)->match = true;
            (set->elements + curindex + 1)->len = ss;
            (set->elements + curindex + 1)->s = target;
            (set->elements + curindex + 1)->p = start;

            (set->elements + curindex)->match = false;
            (set->elements + curindex)->len -= ss;

        }
        else{// 三断
            memmove(set->elements + curindex, set->elements + curindex + 2,
                    sizeof(set->elements[0]) * (index - curindex));


            (set->elements + curindex + 1)->match = true;
            (set->elements + curindex + 1)->len = ss;
            (set->elements + curindex + 1)->s = target;
            (set->elements + curindex + 1)->p = start;

            (set->elements + curindex + 2)->match = false;
            (set->elements + curindex + 2)->len = 
                (set->elements + curindex)->len - ss - (target -  (set->elements + curindex)->s) ;
            (set->elements + curindex + 2)->s = target + ss;

            (set->elements + curindex)->match = false;
            (set->elements + curindex)->len -= target -  (set->elements + curindex)->s;
        
        }
        

    };
    return true;

}
