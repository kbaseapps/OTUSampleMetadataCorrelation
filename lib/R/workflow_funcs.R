


dmessage = function(o) {
  dec = '##########'
  message(dec)
  
  if(class(o) == 'character') {
    message( o)
  }
  else if(class(o) == 'data.frame') {
    message(sprintf('DF DIM: %d, %d', dim(df)[1], dim(df)[2]))
  }
  else if(class(o) == 'phyloseq') {
    message(sprintf('NTAXA: %d, NSAMPLES: %d', ntaxa(ps), nsamples(ps)))
  }
  else {
    message(sprintf('object type %s not supported', class(o)))
    message('value is')
    message(o)
  }
}


dprint = function(s) {
  if(debug) print(s)
}

################################################################################
cat_heading = function(title, lvl=2){
  cat(paste0('\n\n', '## ', title, '\n\n'))
}

################################################################################
cat_text = function(text) {
  cat(paste0('\n\n', text, '\n\n'))
}



################################################################################
big_red_exit = function(msg) {
################################################################################
  knitr::knit_exit(
    paste0(
      '\n\n# {-}\n\n',
      '<h3 style="color:red">',
      msg,
      '</h3>'
    )
  )
}

