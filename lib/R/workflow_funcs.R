

debug = TRUE


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
  }
}

# dmessage_ps = function(ps) {
#   message(sprintf('NTAXA: %d, NSAMPLES: %d', ntaxa(ps), nsamples(ps)))
# }
# 
# dmessage_df(df) {
#   message(sprintf('DIM: %d, %d'), dim(df)[1], dim(df)[2])
# }

dprint = function(s) {
  if(debug) print(s)
}


cat_header = function(title, lvl=2){
  cat(paste('##', title, '\n\n'))
}

cat_text = function(text) {
  cat(paste0('\n', text, '\n'))
}

colored = function(text, color='red') {
  paste0('<p style="color:', color, '">', text, '</p>')
}

titled = function(text, h=3) {
  sprintf('<h%d>%s</h%d>', h, text, h)
}

big_red = function(text) {
  titled(colored(text))
}



# ###################
# get_new_drop = function(droptab, rnew, cnew) {
# ###################
#   num_entries = dim(droptab)[2] # num columns in droptab
#   num_row_dropped = if(num_entries==1) 0 else sum(droptab[1,-1]) # num already dropped
#   num_col_dropped = if(num_entries==1) 0 else sum(droptab[2,-1]) # num already dropped
#   
#   rdrop = droptab[1,1] - num_row_dropped - rnew # num dropped this time
#   cdrop = droptab[2,1] - num_col_dropped - cnew # num dropped this time
#   
#   c(rdrop, cdrop)
# }



############################
# From Michael J Williams at 
# http://michaeljw.com/blog/post/subchunkify/
subchunkify <- function(g, fig_height=7, fig_width=5) {
############################
  g_deparsed <- paste0(deparse(
    function() {g}
  ), collapse = '')
  
  sub_chunk <- paste0("
  `","``{r sub_chunk_", floor(runif(1) * 10000), ", fig.height=", fig_height, ", fig.width=", fig_width, ", echo=FALSE}",
                      "\n(", 
                      g_deparsed
                      , ")()",
                      "\n`","``
  ")
  
  cat(knitr::knit(text = knitr::knit_expand(text = sub_chunk), quiet = TRUE))
}

############################
is_empty = function(mat) {
############################
  # check if dim is (0,0)
  # or just all NA
  
  if(ncol(mat)==0 && nrow(mat)==0) return(TRUE)
  if(all(is.na(mat))) return(TRUE)
  
  return(FALSE)
}


############################
kable_droptab = function(droptab) {
############################
  print(kable(droptab, caption="Amplicon matrix's starting dimensions and subsequent effects"))
}

############################
lowest_rank = function(t) {
############################
  ranks = colnames(t)

  for(rnk in rev(ranks)) {
    if(!all(is.na(t[,rnk]))) {
      return(rnk)
    }
  }

  return(NA)
}

############################
drop_NA_cols = function(t) {
############################
  # drop cols of tax table that are all NA

  ranks = colnames(t)
  rnk = lowest_rank(t)

  if(is.na(rnk)) return(NA)

  c = which(ranks == rnk) # last non-all-NA col
  t = t[,1:c] # subset good cols

  return(t)
}

############################
cat_tax = function(t) {
############################
  t = t[,complete.cases(t(t))]

  t[which(is.na(t))] = '' # fill leftover NAs
  apply(t, MARGIN=1, function(row) paste(row, collapse=';'))
}


############################
wrap_taxstr = function(taxstr, len) {
###########################
  taxstr = stringr::str_replace_all(taxstr, ';', '; ')
  taxstr = stringr::str_wrap(taxstr, width=len)
  taxstr = stringr::str_replace(taxstr, ' ', '')
}


############################
summarize_tab = function(tab, title='title', pool=TRUE, kblsmm=TRUE) {
############################
  dprint('Start running summarize_tab')
  
  max_subplots = 9
  
  df = as.data.frame(tab);# print(colnames(df)[1:10])
  title = paste(title, sprintf('dim=(%d, %d)', nrow(df), ncol(df)), sep=',\n')
  
  pool = pool & ncol(df)>1
  dfpooled = if(pool) data.frame(pooled=c(t(df))) else NA
  
  ############################
  # cowplot title, pooled hist, and hist of cols 1-c, and ellipsis
  cowplot_df_hists = function(df, c, title) {
  ############################
    dprint('Start running cowplot_df_hists')
    ############################
    # list of ggplots
    # 1 for each col
    df2ggplots = function(df) {
    ############################
      dprint('Start running df2ggplots')
      
      subplots = lapply(names(df), function(nm) {
        p = ggplot(df) + aes_(as.name(nm)) + geom_histogram(bins=30) # specify num bins to avoid warnings
        p = p + geom_vline(xintercept=quantile(df[[nm]], c(0.25,0.5,0.75), na.rm=TRUE), color=c('red', 'green', 'blue'))
        if(dim(df)[1] > 300) p = p + scale_y_log10()
        p
      })
      return(subplots)
    }
    
    titleplot = ggdraw() + draw_label(title)
    poolplot = if(pool) df2ggplots(dfpooled) else c()
    subplots = df2ggplots(df[,1:c])
    
    plotlist = c(poolplot, subplots)
    
    # wrap with print because knitr can't see nested
    print(plot_grid(titleplot, plotlist=plotlist)) 
  }  
  
  taken = 1 + pool
  
  c = min(ncol(df), max_subplots-taken)
  
  
  
  # hist col-wise
  cowplot_df_hists(df, c, title)
  
  
  if(kblsmm) {    
    sdf = as.data.frame.matrix(summary(df[,1:c]))
    if(pool) {
      orig = colnames(sdf)
      sdf$pooled = summary(data.frame(pooled=c(t(df))))
      sdf = sdf[, append(orig, 'pooled', 0)]
    }
    print(kable(sdf, caption=title))
  }

}



# ############################
# # Don't run this (at least for now)
# # Hard to get right/neat, takes time
# summarize_taxtab = function(ps, rnk='phylum') {
# ############################
#   dprint('Start running summarize_taxtab')
#   
#   pointSize = 0.5
#   textSize = 3
#   spaceLegend = 0.1
#   
#   print(
#     plot_bar(ps, fill=rnk, title=paste('Pooled by', rnk)) + ylab('OTU table unit') + 
#       
#       guides(shape = guide_legend(override.aes = list(size = pointSize)),
#              color = guide_legend(override.aes = list(size = pointSize))) +
#       
#       theme(legend.title = element_text(size = textSize), 
#             legend.text  = element_text(size = textSize),
#             legend.key.size = unit(spaceLegend, "lines"))
#   )
#   
# }


############################
summarize_ps = function(ps, title='Amplicon Matrix', summetdat=TRUE) {
############################
  dprint("Start running summarize_ps")
  
  #print(ps)  <--- this does not look good, so far
  
  o = otu_table(ps)
  m = sample_data(ps)
  cat_header('Amplicon Matrix Summary', lvl=2)
  summarize_tab(o, title) # add '...' for truncated dfs?
  
  if(summetdat) {
    cat_header('Sample Metadata Summary', lvl=2)
    summarize_tab(m, 'Sample Metadata')
  }
}

################################################################################
################################################################################
################################################################################

failed_cortest_spiel = 'Not succeeding in correlation testing could be, for example, because of a standard deviation of 0. Please check the correlation formula and the data.'
