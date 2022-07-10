# API Design

Assume pydatafront server host is `API_URL=localhost:4000`

## Base Type from Python to JavaScript/TypeScript

```ts
export type BaseType = 'int' | 'str' | 'list' | 'dict'
```

## Get list of all functions

```ts
const listURL = new URL('/list', API_URL)
type FunctionPreview = {
    name: string
    path: `/param/${string}`
}
type ListResponse = {
    list: FunctionPreview[]
}
const response: ListResponse = await fetch(listURL, {
    method: 'GET'
}).then(res => res.json())
const {list} = response
list.map(fn => {
    console.assert(typeof fn.name === 'name')
    console.assert(typeof fn.path === 'string')
    console.assert(fn.path.startsWith('/param/'))
})
```

## Get details of one function

```ts
type FnDetailResponse = {
    decorated_params: {
        [key: string]: {
            type: BaseType
            treat_as: 'config' | 'column' | 'cell'
            whitelist?: string[]
            example?: any[]
        }
    }
    output_type: {
        [key: string]: BaseType
    }
    path: `/call/${string}`
    desc: string
}
const fnDetailURL = new URL('/param/xxx', API_URL)
const response = await fetch(fnDetailURL, {
    method: 'GET'
}).then(res => res.json())

console.assert(typeof response.decorated_params === 'object')
console.assert(typeof response.output_type === 'object')
console.assert(typeof response.path === 'string')
console.assert(typeof response.desc === 'string')
```

## Cell a function

```ts
const body = {}
type PostResponseSuccess = {
    // we cannot find a type that describe different responses
    [key: string]: any[]
}
type PostResponseError = {}
const response = await fetch(`/call/xxx`, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: {
        'Content-Type': 'application/json'
    }
}).then(res => res.json())
```
