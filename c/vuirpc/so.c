/**
 *   author       :   丁雪峰
 *   time         :   2014-10-18 09:56:18
 *   email        :   fengidri@yeah.net
 *   version      :   1.0.1
 *   description  :   用于判断patten在string中是否存在并返回相关的信息.
 *
 *   patten形如: 如: BB cc Aa Dd.  由空格分开多个subpatten. 
 *
 *   程序主要分析subpatten 在string 中是否存在与并返回所在的位置.
 *
 *   存在的定义: 这里的字符比较是不同于strstr. subpatten中的小字字母可以匹配大小
 *   写字母. 但是其中的大写字母只能匹配大写字母.
 *
 *   返回结果: 是多个substring. 这些substring 的顺序与在string 中的顺序是相同的. 
 *
 *   当subpatten中有一个不能在string 中找到的情况程序会返回false. 如果subpatten
 *   在string 中的顺序与在patten 中的顺序是相同的时候, 当然如你所愿. 但是当不同
 *   的时候会首先在当前已经分析完并拆分成多段substring中的最后一个substring 中
 *   进行查找. 如果没有找到会历遍所的substring 进行查找. 但是会路过已经match 的
 *   substring. 也就说如果string 中只有一个AA. 但是subpatten 中有两个aa. 这时会
 *   被认定为匹配失败.
 *
 *   TODO:
 *        1. 把对于patten 的分析与字符匹配进行分开. 因为可能会在很多场景下使用一
 *        个patten 对于许多string 进行分析.
 *
 *        2. 返回结果使用链表的情形. 目前使用数组的结构, 当向中间进行插入数据的
 *        时候必须使用memmove这会很慢. 并且数据的使用中并不方便.
 */
#include <stdio.h>
#include <stddef.h>
#include <unistd.h>
#include <stdbool.h>
#include <malloc.h>
#include <string.h>
#define LOGINFO(fmt, ...)   printf(fmt  "\n", ## __VA_ARGS__)

// 用于描述在 match_key 的返回结果集中的一个元素. 
struct so_matched{
    const char *s;  // 
    size_t len;     // 元素长度, 这个长度也必然是pat 的长度
    bool match;     // 是否合符
    size_t index;   // 结果集中的id
    const char *p;  // 对应的pat
};
struct so_setmatched{
    size_t size;
    size_t totle;
    struct so_matched elems[];
};



/**
 * strstrcase -- 在src 中查找pat. 如说明中说过的那样. 小写字母可以匹配大小写.
 *               大写字母只能匹配大写字母.
 * @src: 
 * @len: 
 * @pat: 
 * @size: 
 */
const char * strstrcase(const char *src, size_t len, 
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
            tmp = *p - *(src + offset + f);
            if(0 != tmp && 32 != tmp) break;
            ++offset;
            ++p;
            if (offset >= size) return src  + f;
        }while(1);
        ++f;
    }while(f < len);
    return NULL;
}




/**
 * skipspace -- 返回从pos位置开始, 第一个非空格的字符的指针. 可以是当前字符
 * @pos: 指向字符串
 */
static inline const char *skipspace(const char *pos)
{
    while(' ' == *pos) pos++; 
    return 0 == *pos ? NULL : pos;
}

/**
 * skipchar -- 要求当前指向一个字符
 * @pos: 
 */
static inline const char *skipchar(const char *pos)
{
    while(' ' != *pos && 0 != *pos) pos++; 
    return pos;
}


/**
 * nextword -- 要求当前指向一个字符
 * @pos: 
 */
static inline const char *nextword(const char *pos)
{
    return skipspace(skipchar(pos));
}

static inline int countword(const char *pos)
{
    int index = 0;
    pos = skipspace(pos);
    while(pos)
    {
        ++ index;
        pos = nextword(pos);
    }
    return index;
}

struct so_setmatched *match_init(const char *string, const char *patten)
{
    struct so_setmatched *set;// 用于保存返回结果
    int index;

    index = countword(patten);// 返回patten 中的key 数量
    if (!index) return NULL;
    index = index * 2 + 1;
    set = (struct so_setmatched *)malloc(sizeof(struct so_setmatched) + 
            sizeof(struct so_matched) * index);
    set->totle = index;
    set->size = 1;

    set->elems[0].s = string;
    set->elems[0].len = strlen(string);
    set->elems[0].match = false;
    return set;

}


/**
 * find_match -- 
 * @set: 
 * @start: 
 * @end: 
 *      首先比较最后一个elems 的match是不是true, 如果不就从这个elems 中进行比较.
 *      否则或比较失败就从 
 */
bool find_match(struct so_setmatched * set, const char *start, const char *end)
{
    unsigned int ss, index;// patten word len
    const char *target;
    struct so_matched *elem;

    ss = end - start;
    index = set->size -1;
    elem = set->elems + index;
    if (!elem->match)
    {
        target = strstrcase(elem->s, elem->len, start, ss);
        if (target) goto success;
        else goto loop;
    }
loop:
    for (index=0; index < set->size; ++index)
    {

        elem = set->elems + index;
        if (elem->match) continue;

        target = strstrcase(elem->s, elem->len, start, ss);

        if (target) goto success;
    }
    return false;
success:
    if (ss == elem->len)// 全等
    {
        LOGINFO("eq all");
        elem->match = true;
        elem->p = start;
    }
    if (target == elem->s)// 头对齐
    {
        LOGINFO("eq head");
        if (index < set->size -1)
        {
            memmove(elem + 2, elem + 1,
                    sizeof(set->elems[0]) * (set->size - 1 - index));
        }
        set->size += 1;

        (elem + 1)->match = false;
        (elem + 1)->len = elem->len - ss;
        (elem + 1)->s = elem->s + ss;

        elem->match = true;
        elem->len = ss;
        elem->p = start;
    }
    else if (target + ss == elem->s + elem->len)//尾对齐
    {
        LOGINFO("eq tail");
        if (index < set->size -1)
        {
            memmove(elem + 2, elem + 1,
                    sizeof(set->elems[0]) * (set->size - 1 - index));
        }
        set->size += 1;
        (elem + 1)->match = true;
        (elem + 1)->len = ss;
        (elem + 1)->s = target;
        (elem + 1)->p = start;

        elem->len -= ss;
    }
    else{// 三断
        LOGINFO("eq mid");
        if (index < set->size -1)
        {

            LOGINFO("++++++++++");
            memmove(elem + 3, elem + 1,
                    sizeof(set->elems[0]) * (set->size - 1 - index));
        }
        set->size += 2;

        (elem + 1)->match = true;
        (elem + 1)->len = ss;
        (elem + 1)->s = target;
        (elem + 1)->p = start;

        (elem + 2)->match = false;
        (elem + 2)->len = elem->len - ss - (target -  elem->s) ;
        (elem + 2)->s = target + ss;

        elem->match = false;
        elem->len = target -  elem->s;

    }
    return true;

}
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
    const char *start, *end, *target, *pos;
    struct so_setmatched *set;// 用于保存返回结果

    set = match_init(string, patten);
    if (!set)
    {
        *res = NULL;
        return false;
    }
    printf("---------\n");

    pos = skipspace(patten);
    while(pos){
        start = pos;
        end = skipchar(pos);
        if(!find_match(set, start, end))
        {// 查找失败
            free(set);
            return false;
        }
        pos = skipspace(end);
    };
    *res = set;
    return true;

}
#define TEST 0
#if TEST
int main(int argn, char *argv[])
{
    struct so_setmatched *res;
    const char *string;
    const char *patten;
    unsigned int i; 
    bool r;

    string = argv[1];
    patten = argv[2];
    r = match_key(string, patten, &res);
    printf("string: %s\n", string);
    printf("patten: %s\n", patten);
    if (!r)
    {
        printf("match fiald\n");
        return -1;
    }
    printf("total:%d\n", res->totle);
    for (i = 0; i < res->size; ++i)
    {
        printf("%d:%d  %.*s\n", (res->elems + i)->match,
                (int)(res->elems + i)->len ,
                (int)(res->elems + i)->len ,
                (res->elems + i)->s);
    }
    free(res);


}
#endif

