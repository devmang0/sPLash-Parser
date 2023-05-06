
# TODO List

## Rewriting for flexibility and maintenance

For the sake of ease of maintenance, I am rewriting this project to be more flexible, and easier to maintain. This however highlighted bugs that previouslty weren't noticed, as well as some superfulus code that wasn't  


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

