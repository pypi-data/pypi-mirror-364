import teradataml as tdml

def corr(self, method='pearson'):

    assert method == "pearson", "only pearson is currently supported"
    assert tdml.configure.val_install_location not in ["",None], "set val install location, e.g. `tdml.configure.val_install_location = 'val'` "

    DF_corrmatrix = tdml.valib.Matrix(data=self,
                                      columns=list(self.columns),
                                      type="COR").result

    return DF_corrmatrix