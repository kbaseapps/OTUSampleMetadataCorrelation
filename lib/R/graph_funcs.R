

#################################################################################
cat_tax = function(t) {
#################################################################################
  t = t[,complete.cases(t(t))]
  
  t[which(is.na(t))] = '' # fill leftover NAs
  apply(t, MARGIN=1, function(row) paste(row, collapse=';'))
}


################################################################################
wrap_taxstr = function(taxstr, len) {
################################################################################
  taxstr = stringr::str_replace_all(taxstr, ';', '; ')
  taxstr = stringr::str_wrap(taxstr, width=len)
  taxstr = stringr::str_replace(taxstr, ' ', '')
}




################################################################################
do_hists = function(filtervars, cordf) {
################################################################################
  standoff = 5
  font_size = 10
  
  yaxis = list(
    title=list(
      text='Amplicon occurrence',
      font=list(
        size=font_size
      ),
      standoff=standoff
    )
  )
  if(dim(filtervars)[1] > 300) {
    yaxis['type'] = 'log'
  }
  
  xaxis = list(
    title=list(
      text='Max value',
      font=list(
        size=font_size
      ),
      standoff=standoff
    )
  )
  fig_max_val = plot_ly(x=filtervars$max_vals, type="histogram") %>% layout(xaxis=xaxis, yaxis=yaxis)
  
  xaxis = list(
    title=list(
      text='Standard deviation',
      font=list(
        size=font_size
      ),
      standoff=standoff
    )
  )
  fig_stdv = plot_ly(x=filtervars$stdv, type="histogram") %>% layout(xaxis=xaxis, yaxis=yaxis)
  
  xaxis=list(
    title=list(
      text='Correlation',
      font=list(
        size=font_size
      ),
      standoff=standoff
    )
  )
  if(is.na(cordf)) {
    fig_cor = plotly_empty(type='histogram') %>% layout(xaxis=xaxis, yaxis=yaxis)
  } else {
    fig_cor = plot_ly(x=cordf$cor, type="histogram") %>% layout(xaxis=xaxis, yaxis=yaxis)
  }
  
  # For making spaces between subplots
  fig_empty = plotly_empty()
  h_empty = 0.05
  h_fig = (1-2*h_empty)/3
  
  hists = plotly::subplot(
    fig_max_val, 
    fig_empty,
    fig_stdv, 
    fig_empty,
    fig_cor,
    nrows=5, 
    heights=c(h_fig,h_empty,h_fig,h_empty,h_fig),
    titleX=T, 
    titleY=T
  ) %>% 
    layout(
      showlegend=F
      #  title=title, 
      #  margin=margin
    )
  
  return(hists)
}

################################################################################
do_scatters = function(cordf, cor_method, num_subplots, do_tax) {
  ################################################################################
  if (cor_method == 'kendall') {
    sym = 'τ'
  } else if (cor_method == 'pearson') {
    sym = 'r'
  } else if (cor_method == 'spearman') {
    sym = 'ρ'
  }
  sym = paste0('<i>', sym, '</i>')
  
  font_size = 10
  
  figs = list()
  for(id in row.names(cordf)[1:num_subplots]) {
    anno = if(do_tax) wrap_taxstr(cordf[id,'tax'], len=65) else id
    anno = paste(
      anno, 
      sprintf('%s = %.4g', sym, cordf[id,'cor']), 
      sep='\n'
    )
    anno = paste('<b>', anno, '</b>')
    #  margin = list(
    #    t=200 # individual margin doesn't work?
    #  )
    yaxis = list(
      title=list(
        text='Amplicon value',
        font=list(
          size=font_size
        ),
        standoff=5
      )
    )
    xaxis = list(
      title=list(
        text=colnames(m)[1],
        font=list(
          size=font_size
        ),
        standoff=5
      )
    )
    fig = plot_ly(
      x=m[[1]],
      y=c(o[id]),
      type='scatter',
      mode='markers',
      size=8, # marker size
      alpha=0.5
    ) %>% 
      layout(yaxis=yaxis, xaxis=xaxis) %>% 
      add_annotations(
        text=anno, 
        x=0.5, 
        y=1.05, 
        xref='paper', 
        yref='paper', 
        xanchor='center', 
        yanchor='top', # y is top limit of anno
        showarrow=FALSE,
        font=list(
          size=font_size
        )
      )
    
    figs[[id]] = fig
  }
  
  #title = list(
  #   yref='paper',
  #   y=1.01,
  #  text='Amplicons vs. Sample Metadata'
  #)
  margin = list(
    #  t=90
    #  t=10,
    #  b=3,
    l=10,
    r=10
  )
  scatters = plotly::subplot(
    figs, 
    nrows=r,
    shareX=FALSE,
    shareY=FALSE, # TRUE -> axis will retain scale but points will go off graph
    titleX=TRUE,
    titleY=TRUE
  ) %>% layout(
    #  title=title, 
    margin=margin, # for parent figure
    showlegend=FALSE
  )
  return(scatters)
}