
# TODO List

## Liquid Types

### Refining a function

Intuitively, It feels correct to add all the conditions as is, however

```splash

abs:Int where abs >= 0 ( n:Int ){ (* <- add( z3.Int('abs') >= 0  )  *)

    if( n < 0 ){          (* <- add( z3.Int('n') < 0 ) *)
        return -n;        (* <- add( z3.Int('abs') == -z3.Int('n') )  )
    }

    return n;             (* <- add( z3.Int('abs') == z3.Int('n') ) *)

}

```

